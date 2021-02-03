import os
import json
import logging

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

from calculate_mark import calc_mark

index_to_work = {
    0: "Обзор литературы",
    1: "Опубликованная статья",
    2: "Доклад на конференции",
    3: "Грант / конкурс / программа для ЭВМ / методичка",
    4: "Статья ВАК+",
    5: "Патент",
    6: "Научное руководство дипломниками",
    7: "Практика рецензирования / Обзор новых диссертаций",
    8: "Посещены защиты по специальности",
    9: "Подготовка текста НКР на 100%"
}

work_to_index = {key: value for value, key in index_to_work.items()}


class MyApp:
    def __init__(self, uri="bolt://neo4j:7687",
                 user="neo4j",
                 password="test"):
        print("Rising database...")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        # self.clear_db()

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def add_graduate(self, student_dict):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._add_graduate, student_dict)

            for record in result:
                print(f"Created student with name: {record['g']}")

    @staticmethod
    def _add_graduate(tx, *args):
        query = (
            "CREATE (g:Graduate { id: $id, name: $name, surname: $surname, patronymic: $patronymic, group_number: $group_number, year_of_admission: $year_of_admission, email: $email, login: $login, password: $password}) "
            "RETURN g"
        )
        result = tx.run(query, *args)
        try:
            return [{"g": record["g"]["name"]} for record in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    ############################################

    def new_work(self, student_args, work_args):
        student_id = self.find_student_by_pass(student_args)
        print(0)
        if student_id is None:
            return None
        print(1)
        work_id = self.add_work(work_args)
        print(2)
        self.assosiate_work_and_student(student_id, work_id)
        print("New work was done")
        return True

    def assosiate_work_and_student(self, student_id, work_id):
        with self.driver.session() as session:
            result = session.write_transaction(
                self._assosiate_work_and_student, student_id, work_id)

            for record in result:
                print(f"Assosiated student with id: {record['g']['id']} and work with id: {record['w']['id']}")

            return True

    @staticmethod
    def _assosiate_work_and_student(tx, student_id, work_id):
        query = (
            "MATCH(g:Graduate {id: $student_id})"
            "MATCH(w:Work {id: $work_id})"
            "CREATE (g)-[:DID]->(w) "
            "RETURN g, w"
        )
        result = tx.run(query, student_id=student_id, work_id=work_id)
        try:
            return [{"g": record["g"],
                     "w": record["w"]} for record in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def add_work(self, work_dict):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._add_work, work_dict)

            for record in result:
                print(f"Created work with id: {record['w']['id']}")
            return record['w']['id']

    @staticmethod
    def _add_work(tx, *args):
        query = (
            "CREATE (w:Work { id: $id, semester: $semester, index: $index, link: $link}) "
            "RETURN w"
        )
        result = tx.run(query, *args)
        try:
            return [{"w": record["w"]} for record in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def find_student_by_pass(self, args):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._find_student_by_pass, args)
            print(result)
            try:
                student_id = result[0]['g']['id']
                return student_id
            except:
                return None

    @staticmethod
    def _find_student_by_pass(tx, *args):
        query = (
            "MATCH(g:Graduate {login: $login, password: $password})"
            "RETURN g"
        )
        result = tx.run(query, *args)
        try:
            return [{"g": record["g"]} for record in result]
        except:
            return None

    ##############################################

    def find_student_works_by_name(self, args):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._find_student_by_name, args)
            try:
                student_id = str(result[0]['g']['id'])
                works = session.write_transaction(
                    self._find_students_works, student_id)
                print(works)
                list_to_print = [f"Type: {index_to_work[int(work['w']['index'])]}. " \
                                 f"Semester: {work['w']['semester']}. " \
                                 f"Link: {work['w']['link']}." for i, work in enumerate(works)]
                print(list_to_print)

                stat = {(int(work['w']['index']), int(work['w']['semester'])) for _, work in enumerate(works)}

                mark = calc_mark(stat)
                print(f"Mark is {mark}")
                return list_to_print, mark
            except:
                return ["No results"], '2'

    @staticmethod
    def _find_student_by_name(tx, *args):
        query = (
            "MATCH(g:Graduate {name: $name, surname: $surname, patronymic: $patronymic})"
            "RETURN g"
        )
        result = tx.run(query, *args)
        try:
            return [{"g": record["g"]} for record in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    @staticmethod
    def _find_students_works(tx, student_id):
        print(f"Finding works done by student_id {student_id}")

        cmd = "MATCH (g:Graduate {id: %d})-[:DID]->(w) RETURN w" % int(student_id)
        query = (
            cmd
        )
        result = tx.run(query)
        try:
            return [{'w': record["w"]} for record in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def clear_db(self):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            session.write_transaction(self._clear_db)

    @staticmethod
    def _clear_db(tx):
        query = (
            "MATCH (n)"
            "DETACH DELETE n"
        )
        tx.run(query)

    def export_db(self):
        with self.driver.session() as session:
            session.write_transaction(self._export_db)

    @staticmethod
    def _export_db(tx):
        query = '''CALL apoc.export.csv.all("all.csv", {useTypes:true});'''
        return tx.run(query)

    def import_db(self):
        with self.driver.session() as session:
            session.write_transaction(self._import_db)

    @staticmethod
    def _import_db(tx):
        query = '''LOAD CSV FROM "all.csv"'''
        return tx.run(query)


if __name__ == "__main__":
    url = "bolt://localhost:11003"
    user = "neo4j"
    password = "1234"

    # student = {
    #     'id': student_id,
    #     'name': 'Igor',
    #     'surname': 'Filippov',
    #     'patronymic': 'Sergeevich',
    #     'group_number': 7382,
    #     'year_of_admission': 2016,
    #     'email': 'tmp@mail.ru',
    #     'login': 'RedHash',
    #     'password': '12345678'
    # }
    # student_id += 1
    #
    # work = {
    #     'id': work_id,
    #     'semester': 6,
    #     'index': 5,
    #     'link': 'https://docs.google.com/document/d/1doSuQ7hXO8P6r3WzyJCcH1Koc955AL4egyVXMgqPcQE/edit#',
    # }
    # work_id += 1

    app = MyApp(url, user, password)

    # app.add_graduate(student)
    # app.add_work(work)
    # app.assosiate_work_and_student(0, 0)

    app.clear_db()

    app.close()
