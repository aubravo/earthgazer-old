from luigi import Task, Parameter, LocalTarget
from luigi.contrib.gcs import GCSTarget
from luigi.contrib.bigquery import BigQueryTarget, BigQueryRunQueryTask, BigQueryClient


class MyBigQueryTask(BigQueryRunQueryTask):
    query = 'SELECT * FROM `bigquery-public-data.samples.shakespeare` LIMIT 1000'
    project = 'my-gcp-project'
    dataset_id = 'my_dataset'
    table_id = 'my_table'

    def output(self):
        return BigQueryTarget(
            client=BigQueryClient(
                project=self.project
            ),
            project_id=self.project,
            dataset_id=self.dataset_id,
            table_id=self.table_id
        )

class testTask(Task):
    def requires(self) -> BigQueryRunQueryTask:
        return MyBigQueryTask()

    def run(self):
        with self.output.open('w') as f:
            for row in self.input():
                f.write(str(row) + '\n')

    def output(self):
        return LocalTarget('output.txt')
