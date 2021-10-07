#property strict

/// Freezes execution of the program for the period of `milliseconds`.
void sleep(uint milliseconds)
{
    if (IsTesting())
    {
        uint stop_tick_count = GetTickCount() + milliseconds;

        while (GetTickCount() < stop_tick_count);
    }
    else
        Sleep(milliseconds);
}