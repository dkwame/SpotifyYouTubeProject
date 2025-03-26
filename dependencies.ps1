#always upgrade pip by default
python3.exe -m pip install --upgrade pip
#install regex
$depen1 = python3.exe -m pip freeze | findstr regex
if ($depen1 -notlike '*regex*')
{
    python3.exe -m pip install regex
}

#install google-api-python3-client
$depen2 = python3.exe -m pip freeze | findstr google-api-python3-client
if ($depen2-notlike '*google-api-python*')
{
    python3.exe -m pip install google-api-python3-client
}

#install google-auth-oauthlib 
$depen3 = python3.exe -m pip freeze | findstr google-auth-oauthlib
if ($depen3 -notlike '*google-auth-oauthlib*')
{
    python3.exe -m pip install google-auth-oauthlib
}

#install requests_oauthlib
$depen4 = python3.exe -m pip freeze | findstr requests_oauthlib
if ($depen4 -notlike 'requests_oauthlib')
{
    python3.exe -m pip install requests_oauthlib
}

#install psycopg[binary,pool]
$depen5 = python3.exe -m pip freeze | findstr psycopg
if ($depen5 -notlike 'psycopg-binary')
{
    python3.exe -m pip install "psycopg[binary,pool]"
}