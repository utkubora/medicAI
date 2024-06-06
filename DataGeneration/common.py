from base import StaticClass
from langchain.schema import Document
from json import dumps, loads
import jsonlines
import csv

class CommonModules(StaticClass):
    @classmethod
    def csv_saver(cls, data, path, json_lines=False):
        print(f"Saving documents to {path}...")

        if not isinstance(data, list):
            raise TypeError("data must be a list of Document")
        for doc in data:
            if not isinstance(doc, Document):
                raise TypeError("data must be a list of Document")
        
        headers = ['chunk', 'question', 'answer']

        # Use 'a' mode to append to the existing file
        with open(path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            
            # Check if the file is empty and write headers if needed
            if csvfile.tell() == 0:
                writer.writeheader()
            
            for doc in data:
                row = {
                    'chunk': doc.page_content,
                    'question': doc.metadata['question'],
                    'answer': doc.metadata['answer']
                }
                writer.writerow(row)

        print(f"Saving document to {path}... Done.")

    @classmethod
    def documents_saver(cls, data, path, json_lines=False):
        print(f"Saving documents to {path}...")

        if not isinstance(data, list):
            raise TypeError("data must be a list of Document")
        for doc in data:
            if not isinstance(doc, Document):
                raise TypeError("data must be a list of Document")

        def dumps_func(o, indent=None):
            return dumps(
                o,
                ensure_ascii=False,
                indent=indent,
                default=lambda o: o.__dict__,
            )

        if json_lines:
            with jsonlines.open(path, mode="a", dumps=dumps_func) as writer:
                writer.write_all(data)
        else:
            # Read existing JSON data, if any
            existing_data = []
            try:
                with open(path, "r", encoding="utf-8") as f:
                    existing_data = loads(f.read())
            except FileNotFoundError:
                pass  # If the file doesn't exist, proceed to writing new data

            # Append new data to existing data
            existing_data.extend(data)

            # Write combined data back to the file
            with open(path, "w", encoding="utf-8") as f:
                f.write(dumps_func(existing_data, indent=4))

        print(f"Saving documents to {path}... Done.")

    @classmethod
    def timer(cls, start_time, endtime):
        time_taken = endtime - start_time
        minutes = int(time_taken // 60)  
        seconds = round(time_taken % 60, 3)
        return minutes, seconds