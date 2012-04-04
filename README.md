# Polar Paywall Tester #

This library contains tests that will query a publisher's server and check for
incompatabilities with the supplied version number.

## Installation ##

## Usage ##

## Coverage ##

The testing functions try to exercise all of the potential paths expected to
be implemented in the publisher. This section of the readme describes the test
coverage for the various entry points.

### auth ###

The following tests are run on the auth entry point.

#### url ####

 * Proper API:
  * Correct Value: paywallproxy
  * Expected Result: InvalidAPI 404

 * Correct Version:
  * Correct Value: v1.0.0
  * Expected Result: InvalidVersion 404

 * Correct Format:
  * Correct Value: json
  * Expected Result: InvalidFormat 404

#### headers ####

 * Authorization:
  * Tests:
   * No header.
   * No token.
   * Token incorrect.
  * Correct Value: PolarPaywallProxyAuthv1.0.0
  * resut = InvalidAuthScheme 400

#### body ####

 * Charset
  * Tests:
   * Non-utf8 encoded values.
  * Expected Result: InternalError 500

 * Json Encoding
  * Tests:
   * Correct number of parameters.
  * Expected Result: InvalidFormat 400

 * device:
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

 * auth\_params
  * Tests:
   * Not an object.
   * Values not strings.
  * Expected Result: InvalidAuthParams 400 

#### model ####

 * Invalid username
  * Expected Result: InvalidPaywallCredentials 401

 * invalid password
  * Expected Result: InvalidPaywallCredentials 401

 * invalid account
  * Expected Result: AccountProblem 403

 * invalid product 
  * Expected Result: InvalidProduct 404

### session ###

#### url ####

 * Proper API:
  * Correct Value: paywallproxy
  * Expected Result: InvalidAPI 404

 * Correct Version:
  * Correct Value: v1.0.0
  * Expected Result: InvalidVersion 404

 * Correct Format:
  * Correct Value: json
  * Expected Result: InvalidFormat 404

#### headers ####

 * Authorization:
  * Tests:
   * No header.
   * No token.
   * Token incorrect.
  * Correct Value: PolarPaywallProxySessionv1.0.0 session:<session id>
  * resut = InvalidAuthScheme 400

#### body ####

 * body
  * Tests:
   * Providing a body.
  * Correct Value: No body.
  * Expected Result: InternalError 500

#### model ####

 * invalid account
  * Cannot be tested.
   * Invalid accounts cannot authenticate, so the test will never have a valid session id.
  * Expected Result: AccountProblem 403

 * invalid product 
  * Expected Result: InvalidProduct 404

 * expired session
  * Cannot be tested.
   * Timeout values may be very long, so waiting isn't an option.
  * Expected Result: SessionExpired 401
