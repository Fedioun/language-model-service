/*
Author : Achille Fedioun
Contact : fedioun.achille@gmail.com

Single pass decoding using kaldi as a service
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
#include "fstext/fstext-lib.h"
#include "decoder/faster-decoder.h"
#include "decoder/decodable-matrix.h"
#include "base/timer.h"
#include "lat/kaldi-lattice.h"

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

int main(int argc, char *argv[]) {
  const char *usage = "Single pass decoding using kaldi as a service. The model is loaded only once during the initialization";

  ParseOptions po(usage);
  bool binary = true;
  float loop_period = 0.005;
  BaseFloat acoustic_scale = 0.1;
  bool allow_partial = true;
  std::string log_file = "/var/log/decode-faster-service.log";
  std::string word_syms_filename, input_folder, output_folder, fst_in_filename, alignment_wspecifier;
  FasterDecoderOptions decoder_opts;
  decoder_opts.Register(&po, true);  // true == include obscure settings.
  po.Register("binary", &binary, "Write output in binary mode");
  po.Register("allow-partial", &allow_partial, "Produce output even when final state was not reached");
  po.Register("acoustic-scale", &acoustic_scale, "Scaling factor for acoustic likelihoods");
  po.Register("word-symbol-table", &word_syms_filename, "Symbol table for words [for debug output]");
  po.Register("loop_period", &loop_period, "Time between two probes");

  po.Register("log-file", &log_file, "Log file");
  po.Register("input-folder", &input_folder, "Input folder for loglikes, inputs file must end with \".tra\"");
  po.Register("output-folder", &output_folder, "Output folder for results");
  po.Register("model", &fst_in_filename, "Model");

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
    fputs("Loaded successfully, ready to work !\n", logger);
    fflush(logger);

    while (1) {
      // Dir iterator
      DIR * i_d = opendir(input_folder.c_str());
      struct dirent *folder_itr;

      if (i_d != NULL) {
        while (folder_itr = readdir(i_d)){
          if (hasEnding(string(folder_itr->d_name), ".tra")) {
            fputs("\nStarting decoding on file ", logger);
            fputs(folder_itr->d_name, logger);
            fputs("\n", logger);
            std::string file_name = string(folder_itr->d_name);
            std::string loglikes_rspecifier = "ark,t:" + input_folder + file_name;

            try {
              //fputs((loglikes_rspecifier +"\n").c_str(), logger);

              //fputs((words_wspecifier + "\n").c_str(), logger);


              Int32VectorWriter alignment_writer(alignment_wspecifier);
              fst::SymbolTable *word_syms = NULL;
              if (word_syms_filename != "") {
                word_syms = fst::SymbolTable::ReadText(word_syms_filename);
                if (!word_syms)
                  KALDI_ERR << "Could not read symbol table from file "<< word_syms_filename;
              }

              SequentialBaseFloatMatrixReader loglikes_reader(loglikes_rspecifier);

              // It's important that we initialize decode_fst after loglikes_reader, as it
              // can prevent crashes on systems installed without enough virtual memory.
              // It has to do with what happens on UNIX systems if you call fork() on a
              // large process: the page-table entries are duplicated, which requires a
              // lot of virtual memory.
              //
              // Edit : we do not do this here

              BaseFloat tot_like = 0.0;
              eesen::int64 frame_count = 0;
              int num_success = 0, num_fail = 0;

              FasterDecoder decoder(*decode_fst, decoder_opts);

              Timer timer;

              std::string words_wspecifier = "ark,t:" + output_folder + file_name.substr(0, file_name.find_last_of(".")) + ".tmp";
              Int32VectorWriter words_writer(words_wspecifier);
              for (; !loglikes_reader.Done(); loglikes_reader.Next()) {
                std::string key = loglikes_reader.Key();
                const Matrix<BaseFloat> &loglikes (loglikes_reader.Value());
                if (loglikes.NumRows() == 0) {
                  KALDI_WARN << "Zero-length utterance: " << key;
                  num_fail++;
                  continue;
                }
                DecodableMatrixScaled decodable(loglikes, acoustic_scale);
                decoder.Decode(&decodable);
                VectorFst<LatticeArc> decoded;  // linear FST.
                if ( (allow_partial || decoder.ReachedFinal())
                     && decoder.GetBestPath(&decoded) ) {
                  num_success++;
                  if (!decoder.ReachedFinal())
                    fputs("Decoder did not reach end-state, outputting partial traceback.", logger);
                  std::vector<int32> alignment;
                  std::vector<int32> words;
                  LatticeWeight weight;
                  frame_count += loglikes.NumRows();
                  GetLinearSymbolSequence(decoded, &alignment, &words, &weight);

                  words_writer.Write(key, words);
                  if (alignment_writer.IsOpen())
                    alignment_writer.Write(key, alignment);
                  if (word_syms != NULL) {
                    std::cerr << key << ' ';
                    for (size_t i = 0; i < words.size(); i++) {
                      std::string s = word_syms->Find(words[i]);
                      if (s == "")
                        fputs(("Word-id " + std::to_string(words[i]) + " not in symbol table.").c_str(), logger);
                      if (s == "s6")
                        fputs(" ", logger);
                      else
                        fputs(s.c_str(), logger);
                    }
                    fputs("\n", logger);
                  }
                  BaseFloat like = -weight.Value1() -weight.Value2();
                  tot_like += like;
                  fputs(("Log-like per frame for utterance " + key + " is "\
                            + std::to_string(like / loglikes.NumRows()) + " over "\
                            + std::to_string(loglikes.NumRows()) + " frames.").c_str(), logger);

                } else {
                  num_fail++;
                  fputs(("Did not successfully decode utterance " + key\
                             + ", len = " + std::to_string(loglikes.NumRows())).c_str(), logger);
                }
              }

              double elapsed = timer.Elapsed();
              fputs(("Time taken " + std::to_string(elapsed) + "\n").c_str(), logger);
              fputs(("Done " + std::to_string(num_success) + " utterances, failed for " + std::to_string(num_fail) + "\n").c_str(), logger);
              fputs(loglikes_rspecifier.substr(6, loglikes_rspecifier.size()).c_str(), logger);
              fflush(logger);
              std::string output_name = (words_wspecifier.substr(0, words_wspecifier.find_last_of(".")).substr(6, words_wspecifier.size()) + ".txt");
              fputs(output_name.c_str(), logger);
              int result;
              result = rename(words_wspecifier.substr(6, words_wspecifier.size()).c_str(), output_name.c_str() );
              if ( result == 0 )
                fputs( "File successfully renamed \n", logger );
              else
                fputs( "Error renaming file \n", logger );
              // Remove "ark,t:" at the beginning of the file's name
              remove(loglikes_rspecifier.substr(6, loglikes_rspecifier.size()).c_str());
              delete word_syms;

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
