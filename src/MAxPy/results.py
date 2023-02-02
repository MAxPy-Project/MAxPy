import os.path
import csv

class ResultsTable:
    def __init__(self, filepath=None, quality_metrics=[]):
        if filepath is None:
            print(f"{self.__class__.__name__} error! invalid filepath input!")
        elif os.path.isfile(filepath):
            print(f"{self.__class__.__name__} file {filepath} already exists, skipping creation")
            self.filepath = filepath
        else:
            with open(filepath, "w") as file_handle:
                print(f"{self.__class__.__name__} creating file {filepath}")
                self.filepath = filepath
                header_base = "circuit;area;power;timing;"
                header_metrics = ";".join(quality_metrics)
                header_final = header_base + header_metrics + "\r\n"
                file_handle.write(header_final)

    def add(self, ckt, results_dict):
        with open(self.filepath, "r") as csvfile:
            csv_content = csv.reader(csvfile, delimiter=";")
            header_line = next(csv_content)
        with open(self.filepath, "a") as csvfile:
            dict_writer = csv.DictWriter(csvfile, fieldnames=header_line, delimiter=";")
            new_info = {
                "circuit": ckt.parameters,
                "area": f"{ckt.area:.4f}",
                "power": f"{ckt.power:.4f}",
                "timing": f"{ckt.timing:.4f}",
                }
            new_info.update(results_dict)
            dict_writer.writerow(new_info)
