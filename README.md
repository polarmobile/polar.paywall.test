# Polar Paywall Tester #

This tool runs tests that will query a publisher's server and check for
incompatibilities with the polar api.

## Installation ##

In order to use this tool you will first need to first install python2.5, 2.6
or 2.7. You then need to install setuptools for your respective version of
python.

Once these packages are installed, run the setup.py command:

    python setup.py install

This command will install the source and binaries required to run the tool.

### Windows ###

On windows, the tool will be installed under the directory:

    C:\Python2.X\Scripts\paywall.test.exe

### Linux / Mac ###

On Mac and Linux, python should install the paywall.test to the system's path.
You will be able to call the utility directly on the command line.

## Usage ##

Open a command terminal and be sure you can run the paywall.test script. When
run directly, the script will print out help information. You must first
configure the application before you run it.

### Configuration ###

To generate a sample configuration run the command:

    paywall.test template

This command will print the sample configuration to the console. To save it to
a file, run the command:

    paywall.test template > config

Edit the sample configuration. You will need to specify the address of the
server. If the server is running on a different port, you can specify the
port using the following syntax:

    address = localhost:8080

In order to successfully run the tests, you need to specify at a __server__,
a __valid user__ and a set of __products__ as sections in the configuration.
You may optionally specify an __invalid user__ for additional tests.

### Testing ###

You have the option of testing the entry points independently or running the
full suite of tests. To run all of the tests use the command:

    paywall.test all config 

Where config is the name of the configuration file. By default, the command
will only report violations to the API. You can increase the log level to
get more information on the types of tests being run:

    paywall.test all config -l info

While it is not necessary that all of the tests pass validation, fewer failures
will reduce the chance of failures occurring in production.

## Coverage ##

The testing functions try to exercise all of the potential paths expected to
be implemented in the publisher. This section of the readme describes the test
coverage for the various entry points. There are a number of entry points that
cannot be tested and they are noted.

### auth ###

The following tests are run on the auth entry point.

#### URL ####

##### Proper API: #####
 * Correct Value: paywallproxy
 * Expected Result: InvalidAPI 404

##### Correct Version: #####
 * Correct Value: v1.0.0
 * Expected Result: InvalidVersion 404

##### Correct Format: #####
 * Correct Value: json
 * Expected Result: InvalidFormat 404

#### Headers ####

##### Authorization: #####
 * Tests:
  * No header.
  * No token.
  * Token incorrect.
 * Correct Value: PolarPaywallProxyAuthv1.0.0
 * result = InvalidAuthScheme 400

#### Body ####

##### Charset #####
 * Tests:
  * Non-utf8 encoded values.
 * Expected Result: InternalError 500

##### Json Encoding #####
 * Tests:
  * Correct number of parameters.
 * Expected Result: InvalidFormat 400

##### device: #####
 * Tests:
  * device not in body.
  * Is an object.
  * manufacturer not in device.
  * manufacturer not a string.
  * model not in device.
  * model not a string.
  * os\_version not in device.
  * os\_version not a string.
 * Expected Result: InvalidDevice 400

##### auth\_params #####
 * Tests:
  * Not an object.
  * Values not strings.
 * Expected Result: InvalidAuthParams 400 

#### Model ####

##### Invalid username #####
 * Expected Result: InvalidPaywallCredentials 401

##### Invalid password #####
 * Expected Result: InvalidPaywallCredentials 401

##### Invalid account #####
 * Expected Result: AccountProblem 403

##### Invalid product  #####
 * Expected Result: InvalidProduct 404

### session ###

#### URL ####

##### Proper API: #####
 * Correct Value: paywallproxy
 * Expected Result: InvalidAPI 404

##### Correct Version: #####
 * Correct Value: v1.0.0
 * Expected Result: InvalidVersion 404

##### Correct Format: #####
 * Correct Value: json
 * Expected Result: InvalidFormat 404

#### Headers ####

##### Authorization: #####
 * Tests:
  * No header.
  * No token.
  * Token incorrect.
 * Correct Value: PolarPaywallProxySessionv1.0.0 session:<session id>
 * result = InvalidAuthScheme 400

#### Body ####

 * Tests:
  * Providing a body.
 * Correct Value: No body.
 * Expected Result: InternalError 500

#### Model ####

##### Invalid Account #####
 * Cannot be tested.
  * Invalid accounts cannot authenticate, so the test will never have a valid session id.
 * Expected Result: AccountProblem 403

##### Invalid Product  #####
 * Expected Result: InvalidProduct 404

##### Expired Session #####
 * Cannot be tested.
  * Timeout values may be very long, so waiting isn't an option.
 * Expected Result: SessionExpired 401
