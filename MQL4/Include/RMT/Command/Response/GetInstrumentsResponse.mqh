#property strict

// 3rdparty
#include <Mql/Collection/Vector.mqh>

// Local
#include "../../Trading/Instrument.mqh"
#include "../../Utility/JsonWriter.mqh"

/// Response:
/// [
///   {
///     "symbol":       string,
///     "desc":         ?string,
///     "bcurrency":    ?string,
///     "qcurrency":    ?string,
///     "mcurrency":    ?string,
///     "ndecimals":    integer,
///     "point":        double,
///     "tickSize":     double,
///     "contractSize": double,
///     "lotStep":      double,
///     "minLot":       double,
///     "maxLot":       double,
///     "minStop":      integer,
///     "freezeLvl":    integer,
///     "spread":       integer
///   }
/// ]
class GetInstrumentsResponse {
public:
    GetInstrumentsResponse()
        : instruments(true)
    {}

    void write(JsonWriter& writer) const
    {
        const int instrument_count = instruments.size();

        for (int i = 0; i < instrument_count; i++)
        {
            JsonWriter  subdoc     = writer.subdocument(i);
            Instrument* instrument = instruments[i];

            if (!instrument.is_complete())
                continue;

            subdoc.write("symbol",       instrument.symbol());
            subdoc.write("desc",         instrument.description());
            subdoc.write("bcurrency",    instrument.base_currency());
            subdoc.write("qcurrency",    instrument.quote_currency());
            subdoc.write("mcurrency",    instrument.margin_currency());
            subdoc.write("ndecimals",    instrument.decimal_places());
            subdoc.write("point",        instrument.point());
            subdoc.write("tickSize",     instrument.tick_size());
            subdoc.write("contractSize", instrument.contract_size());
            subdoc.write("lotStep",      instrument.lot_step());
            subdoc.write("minLot",       instrument.min_lot());
            subdoc.write("maxLot",       instrument.max_lot());
            subdoc.write("minStop",      instrument.stop_level());
            subdoc.write("freezeLvl",    instrument.freeze_level());
            subdoc.write("spread",       instrument.spread());
        }
    }

    Vector<Instrument*> instruments;
};