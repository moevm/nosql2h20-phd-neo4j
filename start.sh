#!/bin/bash

set -e

host="neo4j"
port="7474"
cmd="$@"

until curl http://"$host":"$port"; do
  >&2 echo "neo4j is unavailable - sleeping"
  sleep 5
done

>&2 echo "neo4j is up"
exec $cmd

 def export_db(self):
        with self.driver.session() as session:
            session.write_transaction(self._export_db)
            # res, cols = db.cypher_query()
            # with open('files/db.csv', 'w', encoding='utf-8') as f:
            #     print(res[0][4], file=f)
            print(os.listdir())

    @staticmethod
    def _export_db(tx):
        query = '''CALL apoc.export.csv.all(./db.csv)'''
        return tx.run(query)