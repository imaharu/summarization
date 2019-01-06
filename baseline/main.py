import torch
import torch.nn.functional as F
import torch.optim as optim
from torch.nn.utils.rnn import *
# model
from model import *

# hyperparameter
from define import *

# Other
import time
import os
from tqdm import tqdm

def train(model, source_doc, target_doc):
    loss = 0
    loss = model(source_doc.cuda(), target_doc.cuda())
    return loss

if __name__ == '__main__':
    start = time.time()
    device = "cuda:0"

    data_set = MyDataset(article_data, summary_data)
    train_iter = DataLoader(data_set, batch_size=batch_size, collate_fn=data_set.collater, shuffle=True)

    model = EncoderDecoder(source_size, target_size, hidden_size).cuda()
    model.train()
    optimizer = torch.optim.Adagrad( model.parameters(), lr=0.15,  initial_accumulator_value=0.1)

    for epoch in range(args.epoch):
        tqdm_desc = "[Epoch{:>3}]".format(epoch)
        tqdm_bar_format = "{l_bar}{bar}|{n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
        tqdm_kwargs = {'desc': tqdm_desc, 'smoothing': 0.1, 'ncols': 100,
                    'bar_format': tqdm_bar_format, 'leave': False}
        for iters in tqdm(train_iter, **tqdm_kwargs):
            optimizer.zero_grad()
            loss = train(model, iters[0], iters[1])
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 2.0)
            optimizer.step()

        if (epoch + 1)  % 1 == 0 or epoch == 0:
            outfile = "trained_model/" + str(args.save_path) \
                + "-epoch-" + str(epoch + 1) +  ".model"
            torch.save(model.state_dict(), outfile)
            elapsed_time = time.time() - start
            print("時間:",elapsed_time / 60.0, "分")
