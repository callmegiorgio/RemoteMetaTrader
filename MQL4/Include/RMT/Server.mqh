#property strict

// 3rdparty
#include <Zmq/Zmq.mqh>
#include <Zmq/Errno.mqh>

// Local
#include "ServerSocket.mqh"

/// TODO
class Server {
public:
    Server(string shared_name);

    ~Server();

    bool run(string protocol, string hostname, int rep_port, int push_port);

    void stop();
    
    /// TODO
    bool recv_request(string& request);
    bool send_response(string response);

    bool send_ticks(const string& message[]);

private:
    static int last_error_number();
    static string last_error_message();

    bool start_rep_socket(string addr);
    bool start_push_socket(string addr);

    void stop_rep_socket();
    void stop_push_socket();

    Context m_ctx;
    ServerSocket m_rep_socket;
    ServerSocket m_push_socket;
};

//===========================================================================
// --- Server implementation ---
//===========================================================================
int Server::last_error_number()
{
    return Zmq::errorNumber();
}

string Server::last_error_message()
{
    return Zmq::errorMessage(Zmq::errorNumber());
}

Server::Server(string shared_name)
    : m_ctx(shared_name)
    , m_rep_socket(m_ctx, ZMQ_REP)
    , m_push_socket(m_ctx, ZMQ_PUSH)
{
    m_ctx.setBlocky(false);
}

Server::~Server()
{
    stop();
    m_ctx.shutdown();
    m_ctx.destroy(0);
}

bool Server::run(string protocol, string hostname, int rep_port, int push_port)
{
    const string rep_addr = StringFormat("%s://%s:%d", protocol, hostname, rep_port);
    const string push_addr = StringFormat("%s://%s:%d", protocol, hostname, push_port);

    return start_rep_socket(rep_addr) && start_push_socket(push_addr);
}

bool Server::start_rep_socket(string addr)
{
    if (!m_rep_socket.bind(addr))
    {
        PrintFormat("Could not bind (REP) socket to address '%s': %s", addr, last_error_message());
        return false;
    }

    if (!m_rep_socket.set_send_high_water_mark(1))
    {
        Print("Failed to set Send High Water Mater on (REP) socket");
        return false;
    }

    if (!m_rep_socket.set_linger(0))
    {
        Print("Failed to set linger on (REP) socket");
        return false;
    }

    Print("Listening for incoming requests on (REP) socket: ", addr);
    return true;
}

bool Server::start_push_socket(string addr)
{
    if (!m_push_socket.bind(addr))
    {
        PrintFormat("Could not bind (PUSH) socket to address '%s': %s", addr, last_error_message());
        return false;
    }

    Print("Ready to send messages on (PUSH) socket: ", addr);

    return true;
}

void Server::stop()
{
    stop_rep_socket();
    stop_push_socket();
}

void Server::stop_rep_socket()
{
    if (!m_rep_socket.is_bound())
        return;
    
    Print("Unbinding (REP) socket from address: ", m_rep_socket.address());

    if (!m_rep_socket.unbind())
        Print("Failed to unbind (REP) socket: ", last_error_message());
}

void Server::stop_push_socket()
{
    if (!m_push_socket.is_bound())
        return;

    Print("Unbinding (PUSH) socket from address: ", m_push_socket.address());

    if (!m_push_socket.unbind())
        Print("Failed to unbind (PUSH) socket: ", last_error_message());
}

bool Server::recv_request(string& request)
{
    if (m_rep_socket.recv(request, ZMQ_DONTWAIT))
        return true;

    if (last_error_number() != EAGAIN)
        Print("Could not receive request from (REP) socket: ", last_error_message());

    return false;
}

bool Server::send_response(string response)
{
    if (!m_rep_socket.send(response))
    {
        Print("Could not send response to (REP) socket: ", last_error_message());
        return false;
    }

    return true;
}

bool Server::send_ticks(const string& messages[])
{
    const int n = ArraySize(messages);

    if (n == 0)
        return true;

    const int last_index = (n - 1);
    bool finished_with_failure = false;

    for (int i = 0; i < last_index; i++)
    {
        if (!m_push_socket.send(messages[i], ZMQ_SNDMORE))
            finished_with_failure = true;
        
        Print("sending tick msg: ", messages[i]);
    }

    if (!m_push_socket.send(messages[last_index], ZMQ_DONTWAIT))
        finished_with_failure = true;
    
    Print("sending tick msg: ", messages[last_index]);

    return finished_with_failure;
}