'''import logging
import os
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED

# Define the log directory and make sure it exists
log_dir = 'logs'
archive_dir = 'logs_archive'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
if not os.path.exists(archive_dir):
    os.makedirs(archive_dir)


class LogFileHandler(logging.FileHandler):
    MAX_FILE_SIZE_MB = 100  # Maximum file size in megabytes

    def __init__(self, log_dir, archive_dir, *args, **kwargs):
        self.log_dir = log_dir
        self.archive_dir = archive_dir
        self.current_log_file = None
        self.current_date = None
        self.archive_logs()
        self.set_new_log_file()
        super().__init__(self.current_log_file, *args, **kwargs)

    def set_new_log_file(self):
        timestamp = datetime.now().strftime('%Y-%m-%d')
        self.current_log_file = os.path.join(self.log_dir, f'log_{timestamp}.log')
        self.current_date = datetime.now().strftime('%Y-%m-%d')

    def emit(self, record):
        # Check if the current log file should be rotated
        if (datetime.now().strftime('%Y-%m-%d') != self.current_date or
                os.path.getsize(self.current_log_file) >= self.MAX_FILE_SIZE_MB * 1024 * 1024):
            self.archive_logs()
            self.set_new_log_file()
            self.stream = self._open()

        super().emit(record)

    def archive_logs(self):
        # Archive log files excluding today's log
        today_date = datetime.now().strftime('%Y-%m-%d')
        logs_to_archive = []
        for filename in os.listdir(self.log_dir):
            file_path = os.path.join(self.log_dir, filename)
            if os.path.isfile(file_path) and filename.startswith("log_") and file_path != self.current_log_file:
                logs_to_archive.append(file_path)

        if logs_to_archive:
            # Use a single archive file to store all log files
            archive_file = os.path.join(self.archive_dir, 'logs_archive.zip')

            # Add old log files to the archive
            with ZipFile(archive_file, 'a', ZIP_DEFLATED) as zipf:
                for log_file in logs_to_archive:
                    log_filename = os.path.basename(log_file)
                    log_basename, log_ext = os.path.splitext(log_filename)

                    # Ensure unique filenames within the zip archive
                    count = 1
                    arcname = log_filename
                    while arcname in zipf.namelist():
                        arcname = f"{log_basename}_{count}{log_ext}"
                        count += 1

                    zipf.write(log_file, arcname)
                    os.remove(log_file)


def setup_logger():
    # Define the logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove existing handlers
    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])

    # Create an ArchiveFileHandler
    handler = LogFileHandler(log_dir, archive_dir)

    # Create a formatter and set it for the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    return logger
'''