#property strict

// Local
#include "../../Utility/JsonWriter.mqh"

/// Response:
/// {
///   "desc":         ?string,
///   "bcurrency":    ?string,
///   "qcurrency":    ?string,
///   "mcurrency":    ?string,
///   "ndecimals":    integer,
///   "point":        double,
///   "tickSize":     double,
///   "contractSize": double,
///   "lotStep":      double,
///   "minLot":       double,
///   "maxLot":       double,
///   "minStop":      integer,
///   "freezeLvl":    integer,
///   "spread":       integer
/// }
class GetInstrumentResponse {
public:
    GetInstrumentResponse()
    {
        instrument = NULL;
    }

    ~GetInstrumentResponse()
    {
        if (instrument != NULL)
            delete instrument;
    }

    void write(JsonWriter& writer) const
    {
        writer.write("desc",         instrument.description());
        writer.write("bcurrency",    instrument.base_currency());
        writer.write("qcurrency",    instrument.quote_currency());
        writer.write("mcurrency",    instrument.margin_currency());
        writer.write("ndecimals",    instrument.decimal_places());
        writer.write("point",        instrument.point());
        writer.write("tickSize",     instrument.tick_size());
        writer.write("contractSize", instrument.contract_size());
        writer.write("lotStep",      instrument.lot_step());
        writer.write("minLot",       instrument.min_lot());
        writer.write("maxLot",       instrument.max_lot());
        writer.write("minStop",      instrument.stop_level());
        writer.write("freezeLvl",    instrument.freeze_level());
        writer.write("spread",       instrument.spread());
    }

    Instrument* instrument;
};