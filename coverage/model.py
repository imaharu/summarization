from define import *
from encoder import *
from decoder import *
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.nn.utils.rnn as rnn

class EncoderDecoder(nn.Module):
    def __init__(self, source_size, target_size, opts):
        super(EncoderDecoder, self).__init__()
        self.opts = opts
        self.encoder = Encoder(source_size, self.opts)
        self.decoder = Decoder(target_size, self.opts)

    def forward(self, article_docs=None, summary_docs=None, train=False, generate=False):
        if train:
            loss = 0
            encoder_outputs, encoder_features, hx, cx = self.encoder(article_docs)
            mask_tensor = article_docs.t().gt(PADDING).unsqueeze(-1).float().cuda()
            summary_docs = summary_docs.t()
            coverage_vector = torch.zeros(article_docs.t().size()).unsqueeze(-1).cuda()

            for words_f, words_t in zip(summary_docs[:-1], summary_docs[1:]):
                final_dist, hx, cx, align_weight, next_coverage_vector = self.decoder(
                    words_f, hx, cx, encoder_outputs, encoder_features, coverage_vector, mask_tensor)
                loss += F.cross_entropy(
                   self.decoder.linear(final_dist), words_t , ignore_index=0)

                if self.opts["coverage_vector"]:
                    align_weight = align_weight.squeeze()
                    coverage_vector = coverage_vector.squeeze()
                    step_coverage_loss = torch.sum(torch.min(align_weight, coverage_vector), 0)
                    step_coverage_loss = torch.mean(step_coverage_loss)
                    cov_loss_wt = 1
                    loss += (cov_loss_wt * step_coverage_loss)
                    coverage_vector = next_coverage_vector
            return loss

        elif generate:
            encoder_outputs, encoder_features, hx, cx = self.encoder(article_docs)
            mask_tensor = article_docs.t().gt(PADDING).unsqueeze(-1).float().cuda()
            word_id = torch.tensor( [ target_dict["[START]"] ] ).cuda()
            doc = []
            loop = 0
            coverage_vector = torch.zeros(article_docs.t().size()).unsqueeze(-1).cuda()
            while True:
                final_dist, hx, cx, _, next_coverage_vector = self.decoder(
                    word_id, hx, cx, encoder_outputs, encoder_features, coverage_vector, mask_tensor)

                if self.opts["coverage_vector"]:
                    coverage_vector = next_coverage_vector

                word_id = torch.tensor([ torch.argmax(
                        F.softmax(self.decoder.linear(final_dist), dim=1).data[0]) ]).cuda()
                loop += 1
                if loop >= 200 or int(word_id) == target_dict['[STOP]']:
                    break
                doc.append(word_id.item())
            return doc
