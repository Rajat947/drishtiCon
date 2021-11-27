// Download the helper library from https://www.twilio.com/docs/node/install
// Find your Account SID and Auth Token at twilio.com/console
// and set the environment variables. See http://twil.io/secure
const accountSid = 'AC703d460bf4b66abeddf75e9534a05521';
const authToken = '25ce4d6b1e61ce4f83fec77ed1e2b1ef';
const client = require('twilio')(accountSid, authToken);

client.messages
  .create({
     body: 'This is the ship that made the Kessel Run in fourteen parsecs?',
     from: '+13605030590',
     to: '+919560726231'
   })
  .then(message => console.log(message.sid));
