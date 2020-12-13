'use strict';
const AWS = require('aws-sdk');
AWS.config.update({region: 'us-east-1'});

     
function close(sessionAttributes, fulfillmentState, message) {
    return {
        sessionAttributes,
        dialogAction: {
            type: 'Close',
            fulfillmentState,
            message,
        },
    };
}

function elicit_slot(sessionAttributes, slots, slot_to_elicit, intentName, message) {
  return {
        'sessionAttributes': sessionAttributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intentName,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    };
}

function response(sessionAttributes, fulfillmentState, message) {
    return {
        sessionAttributes,
        dialogAction: {
          type: 'Close',
          fulfillmentState,
          message,
        },
    };
}

 
// --------------- Events -----------------------
 
function dispatch(intentRequest, callback) {
    console.log(`request received for userId=${intentRequest.userId}, intentName=${intentRequest.currentIntent.name}`);
    const intentName = intentRequest.currentIntent.name;
    const sessionAttributes = intentRequest.sessionAttributes;
    const slots = intentRequest.currentIntent.slots;
    const FirstKeyword = slots.FirstKeyword;
    const SecondKeyword = slots.SecondKeyword;
    
    callback(close(sessionAttributes, 'Fulfilled',
    {'contentType': 'PlainText', 'content': 
    `FirstKeyword: ${FirstKeyword}, SecondKeyword: ${SecondKeyword}`}));
}
 
// --------------- Main handler -----------------------
 
// Route the incoming request based on intent.
// The JSON body of the request is provided in the event slot.
exports.handler = (event, context, callback) => {
    try {
        dispatch(event,
            (response) => {
                callback(null, response);
            });
    } catch (err) {
        callback(err);
    }
};
