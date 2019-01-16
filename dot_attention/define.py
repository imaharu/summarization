# my function
# Other
import os
import glob
import torch
import pickle
import argparse
from preprocessing import *

##### args #####
parser = argparse.ArgumentParser(description='Sequence to Sequence Model by using Pytorch')

'''
    epoch
    embed_size
    hidden_size
    dropout
    batch_size
'''

parser.add_argument('--epoch', '-e', type=int, default=35,
                    help='Number of sweeps over the dataset to train')
parser.add_argument('--embed_size', type=int, default=256,
                    help='size of embed size for word representation')
parser.add_argument('--dropout', type=int, default=0.2,
                    help='size of dropout')
parser.add_argument('--hidden_size', type=int, default=256,
                    help='number of hidden units')
parser.add_argument('--batch_size', '-b', type=int, default=50,
                    help='Number of batchsize')

parser.add_argument('--max_article_len', type=int, default=400,
                    help='max article length')
parser.add_argument('--max_summary_len', type=int, default=100,
                    help='max summary length')
'''
related files

    result_path
    model_path
    save_path
    load_article_file
    load_summary_file

'''
parser.add_argument('--result_path', '-r' ,type=str)
parser.add_argument('--model_path', '-m' , type=str)
parser.add_argument('--save_path', '-s' , type=str, default="train")

parser.add_argument('--load_article_file', type=str, default="data/article.pt",
                    help='load article file')
parser.add_argument('--load_summary_file', type=str, default="data/summary.pt",
                    help='load article file')
parser.add_argument('--save_article_file', type=str, default="data/article.pt",
                    help='save article file')
parser.add_argument('--save_summary_file', type=str, default="data/summary.pt",
                    help='save article file')
parser.add_argument('--mode', type=str, default="dubug",
                    help='save debug train evaluate')
parser.add_argument('--save_option', type=str, default="train",
                    help='save option')
args = parser.parse_args()
##### end #####

vocab_path = os.environ['cnn_vocab50000']
preprocess = Preprocess(args.max_article_len, args.max_summary_len)
"""
    source_target dict and size is same
"""
source_dict = preprocess.getVocab(vocab_path)
target_dict = preprocess.getVocab(vocab_path)
source_size = len(source_dict)
target_size = len(target_dict)
if args.mode == "save":
    pardir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    debug = False
    if args.save_option == "train":
        train_src = '{}/{}'.format(pardir, "plain_data/train.txt.src")
        train_tgt = '{}/{}'.format(pardir, "plain_data/train.txt.tgt.tagged")
        print("source data path: {} ".format(train_src))
        print("target data path: {} ".format(train_tgt))
        train_source = preprocess.save(train_src , 0, source_dict, args.save_article_file, debug)
        train_target = preprocess.save(train_tgt , 1, target_dict, args.save_summary_file, debug)
    elif args.save_option == "val":
        val_src = '{}/{}'.format(pardir, "plain_data/val.txt.src")
        print("source data path: {} ".format(val_src))
        val_source = preprocess.save(val_src , 0, source_dict, args.save_article_file, debug)
    elif args.save_option == "test":
        test_src = '{}/{}'.format(pardir, "plain_data/test.txt.src")
        print("source data path: {} ".format(test_src))
        test_source = preprocess.save(test_src , 0, source_dict, args.save_article_file, debug)
    exit()

elif args.mode == "debug":
    hidden_size = 4
    embed_size = 2
    max_epoch = 2
    batch_size = 3
    article_data = preprocess.load("data/dubug_article.pt")[:9]
    summary_data = preprocess.load("data/dubug_summary.pt")[:9]

elif args.mode == "train":
    hidden_size = args.hidden_size
    embed_size = args.embed_size
    max_epoch = args.epoch
    batch_size = args.batch_size
    article_data = preprocess.load(args.load_article_file)
    summary_data = preprocess.load(args.load_summary_file)

elif args.mode == "val_decode":
    hidden_size = args.hidden_size
    embed_size = args.embed_size
    max_epoch = args.epoch
    batch_size = args.batch_size
    article_val_data = preprocess.load("data/val_article.pt")

''' share '''
dropout = args.dropout
#print("source document length : {} ".format(len(article_data)))
#print("target document length : {} ".format(len(summary_data)))
print("hidden_size: {} ".format(hidden_size))
print("embed_size: {} ".format(embed_size))
print("batch_size: {} ".format(batch_size))
print("max epoch: {} ".format(max_epoch))