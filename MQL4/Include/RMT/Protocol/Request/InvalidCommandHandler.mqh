#property strict

// Local
#include "../../Network/MessageHandler.mqh"

class InvalidCommandHandler : public MessageHandler {
private:
    void process() override
    {
        write_result(ERR_USER_UNRECOGNIZED_COMMAND);
    }
};