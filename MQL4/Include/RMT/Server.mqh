#property strict

// 3rdparty
#include <Zmq/Zmq.mqh>

// Local
#include "ServerSocket.mqh"

/// TODO
class Server {
public:
    Server(string shared_name);

    ~Server();

    void run(string protocol, string hostname, int rep_port, int push_port);

    void stop();
    
    ////////////////////////////////////////////////////////////////////////////////
    /// @brief Polls a request from the REP socket.
    ///
    /// The method `PollRequest()` polls any pending request from the PULL socket
    /// and writes it into `request_msg`. Returns `true` if a request was polled,
    /// and `false` otherwise.
    ///
    /// @param request_msg A string reference where the request is written to.
    /// @return `true` if a request was received, and `false` otherwise.
    ///
    ////////////////////////////////////////////////////////////////////////////////
    string read_request();

    bool send_response(string response);
    
    bool send_tick(string message);

private:
    Context m_ctx;
    ServerSocket m_rep_socket;
    ServerSocket m_push_socket;
};

//===========================================================================
// --- Server implementation ---
//===========================================================================
Server::Server(string shared_name)
    : m_ctx(shared_name)
    , m_rep_socket(m_ctx, ZMQ_REP)
    , m_push_socket(m_ctx, ZMQ_PUSH)
{
    m_ctx.setBlocky(false);
}

Server::~Server()
{
    m_ctx.shutdown();
    m_ctx.destroy(0);
}

void Server::run(string protocol, string hostname, int rep_port, int push_port)
{
    m_rep_socket.connect(StringFormat("%s://%s:%d", protocol, hostname, rep_port));
    m_push_socket.connect(StringFormat("%s://%s:%d", protocol, hostname, push_port));
}

void Server::stop()
{
    m_rep_socket.disconnect();
    m_push_socket.disconnect();
}

string Server::read_request()
{
    return m_rep_socket.recv();
}

bool Server::send_response(string response)
{
    return m_rep_socket.send(response);
}

bool Server::send_tick(string message)
{
    return m_push_socket.send(message);
}