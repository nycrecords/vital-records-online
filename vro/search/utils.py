import psycopg2
from elasticsearch.helpers import bulk

from vro.constants import certificate_types
from vro.extensions import es
from vro.settings import DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT, DATABASE_SSLMODE


def recreate():
    """Deletes then recreates the index"""
    es.indices.delete('*', ignore=[400, 404])
    create_index()
    num_success, _ = bulk(es, create_docs(), chunk_size=5000)
    print("Successfully created %s certificates docs." % num_success)

def create_index():
    """Creates indices """
    es.indices.create(
        index='certificates',
        body={
            "settings": {
                "index": {
                    "sort.field": ["cert_type", "year", "last_name", "county"],
                    "sort.order": ["asc", "asc", "asc", "asc"],
                    "sort.missing": ["_last", "_last", "_last", "_last"]
                }
            },
            "mappings": {
                "properties": {
                    "cert_type": {
                        "type": 'keyword',
                    },
                    "number": {
                        "type": 'keyword',
                    },
                    "county": {
                        "type": 'keyword',
                    },
                    "year": {
                        "type": "date",
                        "format": "yyyy"
                    },
                    "first_name": {
                        "type": "keyword"
                    },
                    "last_name": {
                        "type": "keyword"
                    },
                    "full_name": {
                        "type": "keyword"
                    },
                    "display_string": {
                        "type": "keyword"
                    },
                    "spouse_first_name": {
                        "type": "keyword"
                    },
                    "spouse_last_name": {
                        "type": "keyword"
                    },
                    "spouse_name": {
                        "type": "keyword"
                    }
                }
            }

        }
    )

def create_docs():
    """Creates elasticsearch request docs for every certificate"""
    if not es:
        return

    conn = psycopg2.connect(
        dbname=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        sslmode=DATABASE_SSLMODE,
    )
    cursor = conn.cursor("fetch_large_result")

    cursor.execute("""
        SELECT certificates.id,
            certificates.type,
            certificates.number,
            certificates.county,
            certificates.year,
            certificates.first_name,
            certificates.last_name,
            certificates.filename,
            certificates.soundex,
            json_agg(
                json_build_object(
                    'first_name', marriage_data_1.first_name,
                    'last_name', marriage_data_1.last_name,
                    'soundex', marriage_data_1.soundex
                )
            ) AS items
        FROM certificates
            LEFT OUTER JOIN marriage_data AS marriage_data_1 ON certificates.id = marriage_data_1.certificate_id
        WHERE certificates.filename IS NOT NULL
        GROUP BY certificates.id;
    """)

    count = 0

    while True:
        certificates = cursor.fetchmany(size=1000)

        if not certificates:
            break

        for c in certificates:
            if c[5] is not None:
                name = "{} {}".format(c[5], c[6])
            elif c[1] == "marriage_license":
                name = "Not Indexed"
            else:
                name = c[6]

            spouse_name = None
            spouse_first_name = None
            spouse_last_name = None

            # Get spouse metadata to store in index
            if c[1] == certificate_types.MARRIAGE:
                spouse_list = c[9]
                for spouse in spouse_list:
                    if spouse["soundex"] != c[8] or spouse["first_name"] != c[5]:
                        spouse_first_name = spouse["first_name"]
                        spouse_last_name = spouse["last_name"]
                        if spouse_first_name is not None:
                            spouse_name = "{} {}".format(spouse_first_name, spouse_last_name)
                        else:
                            spouse_name = spouse_last_name

            # Check for special character in number
            number = c[2]
            if c[2][-1].isalpha():
                unspaced_number = c[2].replace(" ", "")
                spaced_number = unspaced_number.replace(c[2][-1], " " + c[2][-1])
                number = [unspaced_number, spaced_number]

            yield {
                "_index": "certificates",
                "_id": c[0],
                "_source": {
                    "id": c[0],
                    "cert_type": c[1],
                    "number": number,
                    "county": c[3],
                    "year": c[4],
                    "first_name": c[5],
                    "last_name": c[6],
                    "full_name": name,
                    "display_string": c[7][:-4],
                    "spouse_first_name": spouse_first_name,
                    "spouse_last_name": spouse_last_name,
                    "spouse_name": spouse_name
                }
            }

            count = count + 1
            print("COUNT: ", count)

def delete_doc(certificate_id):
    """Delete a specific doc in the index"""
    es.delete(index="certificates",
              id=certificate_id)
