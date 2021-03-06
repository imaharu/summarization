import argparse
from pyrouge import Rouge155
from define import *

def EvaluateByPyrouge(generate_path, model_dir):
    r = Rouge155()
    r.system_dir = generate_path
    r.model_dir = model_dir
    r.system_filename_pattern = '(\d+).txt'
    r.model_filename_pattern = 'gold_#ID#.txt'
    output = r.convert_and_evaluate()
    print(output)
    output_dict = r.output_to_dict(output)
    return output_dict["rouge_1_f_score"], output_dict["rouge_2_f_score"], output_dict["rouge_l_f_score"]

model_dir = "/home/ochi/Lab/gold_summary/val_summaries"
save_dir = "{}/{}".format("trained_model", args.save_dir)
generate_dir = "{}/{}".format(save_dir , args.generate_dir)
rouge1, rouge2, rougeL = EvaluateByPyrouge(generate_dir, model_dir)
print("rouge1", rouge1)
print("rouge2", rouge2)
print("rougeL", rougeL)
