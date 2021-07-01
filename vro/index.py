from vro.models import Certificate

f = open("test2.txt", "r")

for x in f:
  # Strip \n from line
  x = x.rstrip()

  # Split by /
  x = x.split('/')

  # Check last 3 characters for pdf or PDF
  pdf_check = x[-1][-3:].lower()
  if pdf_check != 'pdf':
    print(x)
    print('NOT A PDF')
    print()
  else:
    print(x)

    # Get certificate type
    cert_type = x[1].lower()
    print(cert_type)

    # Get county
    county = x[2].lower()
    print(county)

    # Get year
    year = int(x[3])
    print(year)

    # Get certificate number
    number = x[4].split('-')[-1]
    number = number.rstrip('.pdf')
    number = number.rstrip('.PDF')
    number = number.lstrip('0')
    print(number)
    print()

    # Create and save certificate
    certificate = Certificate(type_=cert_type, county=county, year=year, number=number)
    certificate.save()

f.close()