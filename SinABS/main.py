import torch
import torch.nn.functional as F
import torch.optim as optim
from torch.nn.utils.rnn import *

# model
from model import *

# my function
from create_sin_dict import *

# hyperparameter
from define_sin import *

# Other
import time

def create_mask(words):
    return torch.cat( [ words.unsqueeze(-1) ] * hidden_size, 1)

def train(encoder, decoder, source_doc, target_doc):
    loss = 0
    es_hx_list = []
    es_mask = []
    ew_hx, ew_cx = encoder.w_encoder.initHidden()
    es_hx, es_cx = encoder.s_encoder.initHidden()
    max_dsn =  max([*map(lambda x: len(x), source_docs )])
    max_dtn =  max([*map(lambda x: len(x), target_docs )])
    for i in range(0, max_dsn):
        ew_hx, ew_cx = es_hx, es_cx
        lines = torch.tensor([ x[i]  for x in source_doc ]).t().cuda(device=device)
        for words in lines:
            before_ew_hx , before_ew_cx = ew_hx , ew_cx
            ew_hx , ew_cx = encoder.w_encoder(words, ew_hx, ew_cx)
            w_mask = create_mask(words)
            ew_hx = torch.where(w_mask == 0, before_ew_hx, ew_hx)
            ew_cx = torch.where(w_mask == 0, before_ew_cx, ew_cx)
        before_es_hx, before_es_cx = es_hx, es_cx
        s_mask = create_mask(lines[0])
        es_hx , es_cx = encoder.s_encoder(ew_hx, es_hx, es_cx)
        es_hx = torch.where(s_mask == 0, before_es_hx, es_hx)
        es_cx = torch.where(s_mask == 0, before_es_cx, es_cx)
        es_hx_list.append(es_hx)
        es_mask.append( torch.cat([ lines[0].unsqueeze(-1) ] , 1).unsqueeze(0))

    es_hx_list = torch.stack(es_hx_list, 0)
    es_mask = torch.cat(es_mask)
    ds_hx, ds_cx = es_hx, es_cx
    inf = torch.full((max_dsn, batch_size), float("-inf")).cuda(device=device)
    inf = torch.unsqueeze(inf, -1)

    for i in range(0, max_dtn):
        if i == 0:
            dw_hx, dw_cx = ds_hx, ds_cx
        else:
            dw_hx, dw_cx = ds_new_hx, ds_cx
        lines = torch.tensor([ x[i]  for x in target_doc ]).t().cuda(device=device)
        # t -> true, f -> false
        lines_t_last = lines[1:]
        lines_f_last = lines[:(len(lines) - 1)]
        for words_f, word_t in zip(lines_f_last, lines_t_last):
            before_dw_hx, before_dw_cx = dw_hx, dw_cx
            dw_hx , dw_cx = decoder.w_decoder(words_f, dw_hx, dw_cx)
            w_mask = create_mask(words_f)
            dw_hx = torch.where(w_mask == 0, before_dw_hx, dw_hx)
            dw_cx = torch.where(w_mask == 0, before_dw_cx, dw_cx)
            loss += F.cross_entropy(decoder.w_decoder.linear(dw_hx), word_t , ignore_index=0)
        before_ds_hx, before_ds_cx = ds_hx, ds_cx
        s_mask = create_mask(lines[0])
        ds_hx , ds_cx = decoder.s_decoder(dw_hx, ds_hx, ds_cx)
        ds_hx = torch.where(s_mask == 0, before_ds_hx, ds_hx)
        ds_cx = torch.where(s_mask == 0, before_ds_cx, ds_cx)
        ds_new_hx = decoder.s_decoder.attention(ds_hx, es_hx_list, es_mask, inf)
    return loss

if __name__ == '__main__':
    start = time.time()
    model = HierachicalEncoderDecoder(source_size, target_size, hidden_size).to(device)
    model.train()
    optimizer = torch.optim.Adam( model.parameters(), weight_decay=0.002)

    for epoch in range(30):
        target_docs = []
        source_docs = []
        print("epoch",epoch + 1)
        indexes = torch.randperm(train_doc_num)[0:10000]
        for i in range(0, train_doc_num, batch_size):
            source_docs = [ get_source_doc(english_paths[doc_num], english_vocab) for doc_num in indexes[i:i+batch_size]]
            target_docs = [ get_target_doc(english_paths[doc_num], english_vocab) for doc_num in indexes[i:i+batch_size]]
            # source_docs
            max_doc_sentence_num =  max([*map(lambda x: len(x), source_docs )])
            source_docs = [ [ s + [ english_vocab["<seos>"] ] for s in t_d ] for t_d in source_docs]
            source_spadding = sentence_padding(source_docs, max_doc_sentence_num)
            source_wpadding = word_padding(source_spadding, max_doc_sentence_num)
            for source in source_wpadding:
                source.append([ english_vocab["<eod>"] ])

            max_doc_target_num =  max([*map(lambda x: len(x), target_docs )])
            # add <teos> to target_docs

            target_docs = [ [ [english_vocab["<bos>"]] + s + [ english_vocab["<teos>"] ] for s in t_d ] for t_d in target_docs]
            target_spadding = sentence_padding(target_docs, max_doc_target_num)
            target_wpadding = word_padding(target_spadding, max_doc_target_num)
            for target in target_wpadding:
                target.extend([ [english_vocab["<bos>"] ,  english_vocab["<eod>"]  ] ] )
            optimizer.zero_grad()
            loss = train(model.encoder, model.decoder, source_wpadding,target_wpadding)
            loss.backward()
            optimizer.step()

        if (epoch + 1)  % 5 == 0:
            outfile = "models/" + str(train_doc_num) + "-" + str(epoch + 1) + ".model"
            torch.save(model.state_dict(), outfile)
        elapsed_time = time.time() - start
        print("時間:",elapsed_time / 60.0, "分")
