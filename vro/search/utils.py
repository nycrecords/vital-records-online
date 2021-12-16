from elasticsearch.helpers import bulk
from sqlalchemy.orm import joinedload

from vro.constants import certificate_types
from vro.extensions import es
from vro.models import Certificate


def recreate():
    """Deletes then recreates the index"""
    es.indices.delete('*', ignore=[400, 404])
    create_index()
    create_docs()

def create_index():
    """Creates indices """
    es.indices.create(
        index='certificates',
        body={
            "settings": {
                "index": {
                    "sort.field": ["cert_type", "year", "last_name", "county"],
                    "sort.order": ["asc", "asc", "asc", "asc"]
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
    certificates = Certificate.query.options(joinedload(Certificate.marriage_data)).filter(Certificate.filename.isnot(None)).all()

    operations = []

    for c in certificates:
        spouse_name = None
        spouse_first_name = None
        spouse_last_name = None

        # Get spouse metadata to store in index
        if c.type == certificate_types.MARRIAGE:
            for spouse in c.marriage_data:
                if c.soundex != spouse.soundex:
                    spouse_first_name = spouse.first_name
                    spouse_last_name = spouse.last_name
                    spouse_name = spouse.name

        operations.append({
            "_op_type": "create",
            "_id": c.id,
            "id": c.id,
            "cert_type": c.type,
            "number": c.number,
            "county": c.county,
            "year": c.year,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "full_name": c.name,
            "display_string": c.display_string,
            "spouse_first_name": spouse_first_name,
            "spouse_last_name": spouse_last_name,
            "spouse_name": spouse_name
        })

    num_success, _ = bulk(
        es,
        operations,
        index="certificates",
        chunk_size=1000,
        raise_on_error=True
    )
    print("Successfully created %s certificates docs." % num_success)

def delete_doc(certificate_id):
    """Delete a specific doc in the index"""
    es.delete(index="certificates",
              id=certificate_id)
