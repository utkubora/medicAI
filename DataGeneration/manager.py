import json
from data_preparation import DataPreparationPipeline
from common import CommonModules


class Manager:

    def __init__(self, config_path):
        with open(config_path) as f:
            config = json.load(f)
        self.prep_args = config["args"]

    def prepare_data(self):

        save_dir = self.prep_args["save_dir_path"]

        self.chunks = DataPreparationPipeline.run(
            file_path=self.prep_args["dir_path"],
            chunk_size=self.prep_args["chunk_size"],
            chunk_overlap=self.prep_args["chunk_overlap"],
            question_pre_context=self.prep_args["question_pre_context"],
            answer_pre_context=self.prep_args["answer_pre_context"],
        )

        print(self.chunks)
        
        CommonModules.documents_saver(self.chunks, save_dir + "documents.json")
        CommonModules.csv_saver(self.chunks, save_dir + "documents.csv")
        return self.chunks