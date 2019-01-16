from define import *
from encoder import *
from decoder import *
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.nn.utils.rnn as rnn

class Hierachical(nn.Module):
    def __init__(self):
        super(Hierachical, self).__init__()
        opts = { "bidirectional": True }
        self.w_encoder = WordEncoder(opts)
        self.s_encoder = SentenceEncoder(opts)
        self.w_decoder = WordDecoder()
        self.s_decoder = SentenceDecoder()

    def forward(self, articles_sentences, summaries_sentences):

        word_hx_outputs = []
        for sentences in articles_sentences:
            hx, cx = self.w_encoder(sentences.cuda())
            word_hx_outputs.append(hx)
        word_hx_outputs = torch.stack(word_hx_outputs, 0)

        s_encoder_outputs, s_hx, s_cx = self.s_encoder(word_hx_outputs)
        loss = 0
        for summaries_sentence in summaries_sentences:
            w_hx, w_cx = s_hx, s_cx
            summaries_sentence = summaries_sentence.t().cuda()
            for words_before, words_after in zip(summaries_sentence[:-1], summaries_sentence[1:]):
                w_hx, w_cx = self.w_decoder(words_before, w_hx, w_cx)
                loss += F.cross_entropy(
                    self.w_decoder.linear(w_hx), words_after , ignore_index=0)
            s_hx, s_cx = self.s_decoder(w_hx, s_hx, s_cx)
        return loss