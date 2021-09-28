#property strict

interface Event {
    string name() const;
    string body() const;
};