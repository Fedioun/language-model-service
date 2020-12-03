/*
Author : Achille Fedioun
Contact : fedioun.achille@gmail.com

Two pass decoding using kaldi as a service
The model is loaded only once at the start
*/
#include <sys/types.h>
#include <sys/stat.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <errno.h>
#include <unistd.h>
#include <syslog.h>
#include <string.h>
#include <iostream>
#include <dirent.h>
#include <execinfo.h>
#include "base/kaldi-common.h"
#include "util/common-utils.h"
//#include "tree/context-dep.h"
//#include "hmm/transition-model.h"
#include "fstext/fstext-lib.h"
#include "decoder/decoder-wrappers.h"
#include "decoder/decodable-matrix.h"
#include "base/timer.h"

#include "decoder/decoder-wrappers.h"
#include "decoder/faster-decoder.h"
#include "lat/lattice-functions.h"

using namespace eesen;
typedef eesen::int32 int32;
using fst::SymbolTable;
using fst::VectorFst;
using fst::StdArc;

// Utility fun
bool hasEnding (std::string const &fullString, std::string const &ending) {
    if (fullString.length() >= ending.length()) {
        return (0 == fullString.compare (fullString.length() - ending.length(), ending.length(), ending));
    } else {
        return false;
    }
}

std::vector<std::string> split(const std::string& s, char delimiter, int nbrpos)
{
   std::vector<std::string> tokens;
   std::vector<std::string> res;
   std::string token;
   std::string start = "";
   std::string end = "";
   std::istringstream tokenStream(s);
   while (std::getline(tokenStream, token, delimiter))
   {
      tokens.push_back(token);
      cout << token << endl;
   }
   cout << std::to_string(tokens.size()) << endl;
  if (nbrpos > -1) {
    for( int i=0; i < tokens.size(); i++){
      if (i > nbrpos) {
        start += tokens[i];
      } else {
        end += tokens[i];
      }
    }
  } else {
    for( int i=0; i < tokens.size(); i++){
      if ( i < tokens.size() + nbrpos) {
        start += tokens[i];
        if (i + 1 != tokens.size() + nbrpos) {
            start += delimiter;
        }
      } else {
        end += tokens[i];
        if (i+1 != tokens.size()) {
          end += delimiter;
        }
      }
    }
  };
  res.push_back(start);
  res.push_back(end);

  return res;
}


int LatgenFaster(
    LatticeFasterDecoderConfig config,
    std::string lattice_wspecifier,
    std::string words_wspecifier,
    std::string alignment_wspecifier,
    std::string feature_rspecifier,
    BaseFloat acoustic_scale,
    bool allow_partial,
    VectorFst<StdArc> * decode_fst,
    fst::SymbolTable *word_syms
  ) {
  bool determinize = config.determinize_lattice;
  CompactLatticeWriter compact_lattice_writer;
  LatticeWriter lattice_writer;
  if (! (determinize ? compact_lattice_writer.Open(lattice_wspecifier)
         : lattice_writer.Open(lattice_wspecifier))) {
           //KALDI_ERR << "Could not open table for writing lattices: "  << lattice_wspecifier;
         }


  Int32VectorWriter words_writer(words_wspecifier);

  Int32VectorWriter alignment_writer(alignment_wspecifier);


  double tot_like = 0.0;
  eesen::int64 frame_count = 0;
  int num_success = 0, num_fail = 0;

  SequentialBaseFloatMatrixReader loglike_reader(feature_rspecifier);
  {
    LatticeFasterDecoder decoder(*decode_fst, config);

    for (; !loglike_reader.Done(); loglike_reader.Next()) {
      std::string utt = loglike_reader.Key();
      Matrix<BaseFloat> loglikes (loglike_reader.Value());
      loglike_reader.FreeCurrent();
      if (loglikes.NumRows() == 0) {
        //KALDI_WARN << "Zero-length utterance: " << utt;
        num_fail++;
        continue;
      }

      DecodableMatrixScaled decodable(loglikes, acoustic_scale);
//          DecodableMatrixScaledMapped decodable(trans_model, loglikes, acoustic_scale);

      double like;
      if (DecodeUtteranceLatticeFaster(
              decoder, decodable, word_syms, utt,
              acoustic_scale, determinize, allow_partial, &alignment_writer,
              &words_writer, &compact_lattice_writer, &lattice_writer,
              &like)) {
        tot_like += like;
        frame_count += loglikes.NumRows();
        num_success++;
      } else num_fail++;
    }
  }
  /*
  KALDI_LOG << "Done " << num_success << " utterances, failed for "
            << num_fail;
  KALDI_LOG << "Overall log-likelihood per frame is " << (tot_like/frame_count) << " over "
            << frame_count<<" frames.";
  */
  if (num_success != 0) return 0;
  else return 1;
}

int LatticeAddPenalty(
  std::string lats_rspecifier,
  std::string lats_wspecifier,
  BaseFloat word_ins_penalty
  ) {
  SequentialCompactLatticeReader clat_reader(lats_rspecifier);
  CompactLatticeWriter clat_writer(lats_wspecifier); // write as compact.

  int64 n_done = 0;

  for (; !clat_reader.Done(); clat_reader.Next()) {
    CompactLattice clat(clat_reader.Value());
    AddWordInsPenToCompactLattice(word_ins_penalty, &clat);
    clat_writer.Write(clat_reader.Key(), clat);
    n_done++;
  }
  return (n_done != 0 ? 0 : 1);
}

int LatticeScale(
  std::string lats_rspecifier,
  std::string lats_wspecifier,
  bool write_compact,
  BaseFloat acoustic_scale,
  BaseFloat inv_acoustic_scale,
  BaseFloat lm_scale,
  BaseFloat acoustic2lm_scale,
  BaseFloat lm2acoustic_scale
  ) {
  int32 n_done = 0;

  KALDI_ASSERT(acoustic_scale == 1.0 || inv_acoustic_scale == 1.0);
  if (inv_acoustic_scale != 1.0)
    acoustic_scale = 1.0 / inv_acoustic_scale;

  std::vector<std::vector<double> > scale(2);
  scale[0].resize(2);
  scale[1].resize(2);
  scale[0][0] = lm_scale;
  scale[0][1] = acoustic2lm_scale;
  scale[1][0] = lm2acoustic_scale;
  scale[1][1] = acoustic_scale;

  if (write_compact) {
    SequentialCompactLatticeReader compact_lattice_reader(lats_rspecifier);
    // Write as compact lattice.
    CompactLatticeWriter compact_lattice_writer(lats_wspecifier);

    for (; !compact_lattice_reader.Done(); compact_lattice_reader.Next()) {
      CompactLattice lat = compact_lattice_reader.Value();
      ScaleLattice(scale, &lat);
      compact_lattice_writer.Write(compact_lattice_reader.Key(), lat);
      n_done++;
    }
  } else {
    SequentialLatticeReader lattice_reader(lats_rspecifier);

    // Write as regular lattice.
    LatticeWriter lattice_writer(lats_wspecifier);

    for (; !lattice_reader.Done(); lattice_reader.Next()) {
      Lattice lat = lattice_reader.Value();
      ScaleLattice(scale, &lat);
      lattice_writer.Write(lattice_reader.Key(), lat);
      n_done++;
    }
  }

  //KALDI_LOG << "Done " << n_done << " lattices.";
  return (n_done != 0 ? 0 : 1);
}

int LatticeBestPath(
  std::string lats_rspecifier,
  std::string transcriptions_wspecifier,
  std::string alignments_wspecifier,
  BaseFloat acoustic_scale,
  BaseFloat lm_scale,
  fst::SymbolTable *word_syms
  ) {
  SequentialCompactLatticeReader clat_reader(lats_rspecifier);

  Int32VectorWriter transcriptions_writer(transcriptions_wspecifier);

  Int32VectorWriter alignments_writer(alignments_wspecifier);

  int32 n_done = 0, n_fail = 0;
  int64 n_frame = 0;
  LatticeWeight tot_weight = LatticeWeight::One();

  for (; !clat_reader.Done(); clat_reader.Next()) {
    std::string key = clat_reader.Key();
    CompactLattice clat = clat_reader.Value();
    clat_reader.FreeCurrent();
    fst::ScaleLattice(fst::LatticeScale(lm_scale, acoustic_scale), &clat);
    CompactLattice clat_best_path;
    CompactLatticeShortestPath(clat, &clat_best_path);  // A specialized
    // implementation of shortest-path for CompactLattice.
    Lattice best_path;
    ConvertLattice(clat_best_path, &best_path);
    if (best_path.Start() == fst::kNoStateId) {
      //KALDI_WARN << "Best-path failed for key " << key;
      n_fail++;
    } else {
      std::vector<int32> alignment;
      std::vector<int32> words;
      LatticeWeight weight;
      GetLinearSymbolSequence(best_path, &alignment, &words, &weight);
      /*
      KALDI_LOG << "For utterance " << key << ", best cost "
                << weight.Value1() << " + " << weight.Value2() << " = "
                << (weight.Value1() + weight.Value2())
                << " over " << alignment.size() << " frames.";
      */
      if (transcriptions_wspecifier != "")
        transcriptions_writer.Write(key, words);
      if (alignments_wspecifier != "")
        alignments_writer.Write(key, alignment);
      if (word_syms != NULL) {
        std::cerr << key << ' ';
        for (size_t i = 0; i < words.size(); i++) {
          std::string s = word_syms->Find(words[i]);
          if (s == "")
            KALDI_ERR << "Word-id " << words[i] <<" not in symbol table.";
          std::cerr << s << ' ';
        }
        std::cerr << '\n';
      }
      n_done++;
      n_frame += alignment.size();
      tot_weight = Times(tot_weight, weight);
    }
  }
  /*
  BaseFloat tot_weight_float = tot_weight.Value1() + tot_weight.Value2();

  KALDI_LOG << "Overall score per frame is " << (tot_weight_float/n_frame)
            << " = " << (tot_weight.Value1()/n_frame) << " [graph]"
            << " + " << (tot_weight.Value2()/n_frame) << " [acoustic]"
            << " over " << n_frame << " frames.";
  KALDI_LOG << "Done " << n_done << " lattices, failed for " << n_fail;
  */
  if (n_done != 0) return 0;
  else return 1;
}

int main(int argc, char *argv[]) {
  const char *usage = "Single pass decoding using kaldi as a service. The model is loaded only once during the initialization";
  float loop_period = 0.005;

  ParseOptions po(usage);
  bool write_compact = true;
  BaseFloat inv_acoustic_scale = 1.0;
  BaseFloat lm_scale = 1.0;
  BaseFloat acoustic2lm_scale = 0.0;
  BaseFloat lm2acoustic_scale = 0.0;
  std::string rootTmp = "ark,t:/tmp";

  LatticeFasterDecoderConfig config;

  BaseFloat acoustic_scale = 0.1;
  BaseFloat word_ins_penalty = 0.0;
  bool allow_partial = true;
  std::string log_file = "/var/log/decode-faster-two-pass-service.log";
  std::string word_syms_filename, input_folder, output_folder, fst_in_filename, alignment_wspecifier;
  FasterDecoderOptions decoder_opts;
  config.Register(&po);
  po.Register("loop_period", &loop_period, "Time between two probes");
  po.Register("log-file", &log_file, "Log file");
  po.Register("input-folder", &input_folder, "Input folder for loglikes, inputs file must end with \".tra\"");
  po.Register("output-folder", &output_folder, "Output folder for results");
  po.Register("model", &fst_in_filename, "Model");

  po.Register("acoustic-scale", &acoustic_scale, "Scaling factor for acoustic likelihoods");
  po.Register("word-symbol-table", &word_syms_filename, "Symbol table for words [for debug output]");
  po.Register("allow-partial", &allow_partial, "If true, produce output even if end state was not reached.");

  // lattice-add-penalty;
  po.Register("word-ins-penalty", &word_ins_penalty, "Word insertion penalty");
  // lattice-scale
  po.Register("write-compact", &write_compact, "If true, write in normal (compact) form.");
  po.Register("inv-acoustic-scale", &inv_acoustic_scale, "An alternative way "
              "of setting the acoustic scale: you can set its inverse.");
  po.Register("lm-scale", &lm_scale, "Scaling factor for graph/lm costs");
  po.Register("acoustic2lm-scale", &acoustic2lm_scale, "Add this times original acoustic costs to LM costs");
  po.Register("lm2acoustic-scale", &lm2acoustic_scale, "Add this times original LM costs to acoustic costs");

  po.Read(argc, argv);

  if (word_syms_filename.empty() or input_folder.empty() or output_folder.empty() or fst_in_filename.empty()) {
    std::cout << usage << std::endl << "Arguments : \n - word-symbol-table \n - input-folder \n - output-folder \n - model\nare mandatory." << std::endl << "For more informations use --help" << std::endl;
    exit(EXIT_FAILURE);
  }
  /* Our process ID and Session ID */
  pid_t pid, sid;

  /* Fork off the parent process */
  pid = fork();
  if (pid < 0) {
          exit(EXIT_FAILURE);
  }
  /* If we got a good PID, then
     we can exit the parent process. */
  if (pid > 0) {
          exit(EXIT_SUCCESS);
  }

  /* Change the file mode mask */
  umask(0);

  /* Open logs */

  FILE * logger;
  logger = fopen(log_file.c_str(), "w");
  if (logger==NULL) {
    std::cout << "\nCannot open logger, quitting..." << std::endl;
    exit(EXIT_FAILURE);
  }

  /* Create a new SID for the child process */
  sid = setsid();
  if (sid < 0) {
          /* Log the failure */
          exit(EXIT_FAILURE);
  }

  /* Change the current working directory */
  if ((chdir("/")) < 0) {
          /* Log the failure */
          exit(EXIT_FAILURE);
  }

  /* Close out the standard file descriptors */
  close(STDIN_FILENO);
  close(STDOUT_FILENO);
  close(STDERR_FILENO);

  fputs("Starting service...\n", logger);

  /* Daemon-specific initialization goes here */
  try {

    fputs("Loading model...\n", logger);
    fflush(logger);
    VectorFst<StdArc> *decode_fst = fst::ReadFstKaldi(fst_in_filename);

    fputs("Loading dictionnary...\n", logger);
    fst::SymbolTable *word_syms = NULL;
    if (word_syms_filename != "")
      if (!(word_syms = fst::SymbolTable::ReadText(word_syms_filename)))
        KALDI_ERR << "Could not read symbol table from file "
                   << word_syms_filename;


    fputs("Loaded successfully, ready to work !\n", logger);
    fflush(logger);

    while (1) {
      // Dir iterator
      DIR * i_d = opendir(input_folder.c_str());
      struct dirent *folder_itr;
      bool debug = true;

      if (i_d != NULL) {
        while (folder_itr = readdir(i_d)){
          if (hasEnding(string(folder_itr->d_name), ".tra")) {
            fputs("\nStarting decoding on file ", logger);
            fputs(folder_itr->d_name, logger);
            fputs("\n", logger);
            std::string file_name = string(folder_itr->d_name);







            std::string loglikes_rspecifier = "ark,t:" + input_folder + file_name;

            try {

              std::vector<std::string> tokens = split(loglikes_rspecifier, '/', -1);
              std::string lattice_wspecifier = rootTmp + "/lats_" + tokens.back();
              std::string words_wspecifier = rootTmp + "/words_" + tokens.back();
              std::string alignment_wspecifier = rootTmp + "/alignments_" + tokens.back();

              if (debug) {
                fputs("Lattices \n", logger);

                fputs(lattice_wspecifier.c_str(), logger);
                fputs(" lattice_wspecifier \n", logger);

                fputs(words_wspecifier.c_str(), logger);
                fputs(" words_wspecifier \n", logger);

                fputs(alignment_wspecifier.c_str(), logger);
                fputs(" alignment_wspecifier \n", logger);

                fputs(loglikes_rspecifier.c_str(), logger);
                fputs(" loglikes_rspecifier \n", logger);


                fflush(logger);
              }
              LatgenFaster(
                 config,
                 lattice_wspecifier,
                 words_wspecifier,
                 alignment_wspecifier,
                 loglikes_rspecifier,
                 acoustic_scale,
                 allow_partial,
                 decode_fst,
                 word_syms
               );

               std::string lats_rspecifier = lattice_wspecifier;
               std::string lats_wspecifier = rootTmp + "/add_pen_" + tokens.back();
               cout << lats_rspecifier << endl;
               cout << lats_wspecifier << endl;

               if (debug) {
                 fputs("Penalty", logger);
                 fputs("\n", logger);
                 fputs(lats_rspecifier.c_str(), logger);
                 fputs("\n", logger);
                 fputs(lats_wspecifier.c_str(), logger);
                 fputs("\n", logger);
                 fflush(logger);
               }
               LatticeAddPenalty(
                 lats_rspecifier,
                 lats_wspecifier,
                 word_ins_penalty
               );

               lats_rspecifier = lats_wspecifier;
               lats_wspecifier = rootTmp + "/scale_" + tokens.back();

               cout << lats_rspecifier << endl;
               cout << lats_wspecifier << endl;

               if (debug) {
                 fputs(lats_rspecifier.c_str(), logger);
                 fputs("\n", logger);
                 fputs(lats_wspecifier.c_str(), logger);
                 fputs("\n", logger);
                 fputs("Scale", logger);
                 fflush(logger);
               }
               LatticeScale(
                 lats_rspecifier,
                 lats_wspecifier,
                 write_compact,
                 acoustic_scale,
                 inv_acoustic_scale,
                 lm_scale,
                 acoustic2lm_scale,
                 lm2acoustic_scale
               );

               lats_rspecifier = lats_wspecifier;
               std::vector<std::string> nameTokens = split(tokens.back(), '.', -1);
               lats_wspecifier = "ark,t:" + output_folder + nameTokens[0] + ".txt";

               LatticeBestPath(
                 lats_rspecifier,
                 lats_wspecifier,
                 alignment_wspecifier,
                 acoustic_scale,
                 lm_scale,
                 word_syms
               );

               remove(loglikes_rspecifier.substr(6, loglikes_rspecifier.size()).c_str());

            } catch(const std::exception &e) {
              // Remove "ark,t:" at the beginning of the file's name
              remove(loglikes_rspecifier.substr(6, loglikes_rspecifier.size()).c_str());

              fputs("An error occured : ", logger);
              fputs( e.what(), logger);

              fputs("\n", logger);
              fflush(logger);
            }
          }
        }

      }
      closedir(i_d);
      // fputs( "End of cycle \n", logger);
      fflush(logger);
      sleep(loop_period);

    }
    delete decode_fst;
  } catch(const std::exception &e) {
    fputs( e.what(), logger);
    fputs("\n Quitting...", logger);
    fflush(logger);
    return -1;
  }
  fputs(" You shouldn't reach this", logger);
  fflush(logger);
  exit(EXIT_FAILURE);
}
