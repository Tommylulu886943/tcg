import zipfile
import datetime
import os

class FileOperation:

    @classmethod
    def decompress_configs(cls, input_filename: str) -> None:
        current_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        with zipfile.ZipFile(input_filename, 'r') as zf:
            zf.extractall(current_path)

    @classmethod
    def compress_configs(cls, output_directory: str) -> None:
        now = datetime.datetime.now()
        output_filename = now.strftime("TCG_%Y-%m-%d-%H-%M-%S") + '.zip'
        output_path = os.path.join(output_directory, output_filename)
        
        files = []
        include_dirs = ['./artifacts', './schemas', './config']
        for _dir in include_dirs:
            for root, dirs, filenames in os.walk(_dir):
                for filename in filenames:
                    files.append(os.path.join(root, filename)) 
                           
        with zipfile.ZipFile(output_path, 'w') as zf:
            for file in files:
                zf.write(file)
                