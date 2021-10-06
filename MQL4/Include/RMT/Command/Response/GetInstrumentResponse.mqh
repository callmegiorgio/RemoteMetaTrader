#property strict

// Local
#include "../../Utility/JsonWriter.mqh"
#include "../../Utility/Optional.mqh"

/// Response:
/// {
///   "desc":       ?string,
///   "bcurrency":  ?string,
///   "pcurrency":  ?string,
///   "mcurrency":  ?string,
///   "ndecimals":  integer,
///   "point":      double,
///   "ticksz":     double,
///   "contractsz": double,
///   "lotstep":    double,
///   "minlot":     double,
///   "maxlot":     double,
///   "minstop":    integer,
///   "freezelvl":  integer,
///   "spread":     integer
/// }
class GetInstrumentResponse {
public:
    void write(JsonWriter& writer) const
    {
        writer.write("desc",       this.description);
        writer.write("bcurrency",  this.base_currency);
        writer.write("pcurrency",  this.profit_currency);
        writer.write("mcurrency",  this.margin_currency);
        writer.write("ndecimals",  this.decimal_places);
        writer.write("point",      this.point);
        writer.write("ticksz",     this.tick_size);
        writer.write("contractsz", this.contract_size);
        writer.write("lotstep",    this.lot_step);
        writer.write("minlot",     this.min_lot);
        writer.write("maxlot",     this.max_lot);
        writer.write("minstop",    this.min_stop_level);
        writer.write("freezelvl",  this.freeze_level);
        writer.write("spread",     this.spread);
    }

    Optional<string> description;
    Optional<string> base_currency;
    Optional<string> profit_currency;
    Optional<string> margin_currency;
    long             decimal_places;
    double           point;
    double           tick_size;
    double           contract_size;
    double           lot_step;
    double           min_lot;
    double           max_lot;
    long             min_stop_level;
    long             freeze_level;
    long             spread;
};