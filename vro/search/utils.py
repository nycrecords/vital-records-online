from elasticsearch.helpers import bulk
from sqlalchemy.orm import joinedload

from vro.constants import certificate_types
from vro.extensions import es
from vro.models import Certificate, MarriageData


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
                    }
                }
            }

        }
    )

def create_docs():
    """Creates elasticsearch request docs for every certificate"""
    if not es:
        return
    certificates = Certificate.query.options(joinedload(Certificate.marriage_data)).filter(Certificate.filename.isnot(None)).limit(10000).all()

    # certificates = Certificate.query.join(MarriageData).filter(Certificate.filename.isnot(None)).limit(10000).all()

    operations = []

    # operations.append({
    #     "_op_type": "create",
    #     "_id": c.id,
    #     "cert_type": c.type,
    #     "county": c.county,
    #     "month": c.month,
    #     "day": c.day,
    #     "year": c.year,
    #     "number": c.number,
    #     "first_name": c.first_name,
    #     "last_name": c.last_name,
    #     "age": c.age,
    #     "soundex": c.soundex,
    #     "path_prefix": c.path_prefix,
    #     "filename": c.filename
    # })

    for c in certificates:
        spouse_name = None

        if c.type == certificate_types.MARRIAGE:
            for spouse in c.marriage_data:
                if c.soundex != spouse.soundex:
                    spouse_name = spouse.name
            # for spouse in c.marriage_data.all():
            #     spouse_name = spouse.name

        operations.append({
            "_op_type": "create",
            "_id": c.id,
            "id": c.id,
            "cert_type": c.type,
            "county": c.county,
            "year": c.year,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "full_name": c.name,
            "display_string": c.display_string,
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
