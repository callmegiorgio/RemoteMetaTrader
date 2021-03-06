#property strict

/// Represents a JSON type stored by `JsonValue`.
enum JsonType {
    JSON_UNDEFINED,
    JSON_NULL,
    JSON_BOOL,
    JSON_INTEGER,
    JSON_DOUBLE,
    JSON_STRING,
    JSON_ARRAY,
    JSON_OBJECT
};

/// Stores a JSON value.
class JsonValue {
public:
    /////////////////////////////////////////////////////////////////////////////
    /// @brief Deserializes a JSON string into a `JsonValue` object.
    ///
    /// Deserializes a JSON string and returns the corresponding object. If
    /// deserialization fails, returns a default-constructed `JsonValue` object.
    ///
    /// @return A `JsonValue` object resulting from the deserialization.
    /// @see `type()`
    ///
    /// @code
    /// JsonValue json_obj = JsonValue::deserialize("{ \"hello\": \"world\" }");
    /// if (json_obj)
    ///     Print("Deserialization succeeded!");
    /// else
    ///     Print("Deserialization failed...");
    /// @encode
    ///
    /////////////////////////////////////////////////////////////////////////////
    static JsonValue deserialize(string json_str);

    /// Constructs an object with a type.
    JsonValue(JsonType type = JSON_UNDEFINED);
    
    /// Copy-constructs an object.
    JsonValue(const JsonValue& other);
    
    /// Destroys an object.
    ~JsonValue();
    
    /////////////////////////////////////////////////////////////////////////////
    /// @brief Finds a JSON value by key in a JSON object.
    ///
    /// If `type()` is `JSON_OBJECT` and the JSON object contains `key`, returns
    /// a pointer to the JSON value associated with that key. Otherwise, returns
    /// `NULL`.
    ///
    /// @param A string key.
    /// @return Pointer to JSON value associated with `key` if `key` exists, and
    ///         `NULL` otherwise.
    ///
    /////////////////////////////////////////////////////////////////////////////
    JsonValue* find(string key) const;
    
    /////////////////////////////////////////////////////////////////////////////
    /// @brief Finds a JSON value by index in a JSON array.
    ///
    /// If `type()` is `JSON_ARRAY` and the JSON array contains `index`, returns
    /// a pointer to the JSON value that is in that index. Otherwise, returns
    /// `NULL`.
    ///
    /// @param An index.
    /// @return Pointer to JSON value at `index` if `index` is valid, and `NULL`
    ///         otherwise.
    ///
    /////////////////////////////////////////////////////////////////////////////
    JsonValue* at(int index) const;
    
    /////////////////////////////////////////////////////////////////////////////
    /// @brief Checks whether the JSON object contains a key.
    ///
    /// If `type()` is `JSON_OBJECT`, returns whether the JSON object contains
    /// a value associated with `key`.
    ///
    /// @param A string key.
    /// @return `true` if `key` exists, and `false` otherwise.
    ///
    /////////////////////////////////////////////////////////////////////////////
    bool contains(string key) const;
    
    /////////////////////////////////////////////////////////////////////////////
    /// Returns the number of elements in a JSON array or JSON object.
    ///
    /// If `type()` is `JSON_OBJECT` or `JSON_ARRAY`, returns the number of
    /// key-value pairs or values, respectively, that it contains. Otherwise,
    /// returns 0.
    ///
    /// @return Number of elements in JSON array or JSON object.
    ///
    /////////////////////////////////////////////////////////////////////////////
    int size() const;
    
    /// Returns the type of the JSON value.
    JsonType type() const;
    
    /////////////////////////////////////////////////////////////////////////////
    /// Converts the JSON value to a native type.
    ///
    /// @{
    bool   to_bool  () const;
    long   to_int   () const;
    double to_double() const;
    string to_string() const;
    /// @}
    /////////////////////////////////////////////////////////////////////////////
    
    /////////////////////////////////////////////////////////////////////////////
    /// Converts the JSON value to a native type with type checking.
    ///
    /// @{
    bool   to_bool  (bool& ok) const;
    long   to_int   (bool& ok) const;
    double to_double(bool& ok) const;
    string to_string(bool& ok) const;
    /// @}
    /////////////////////////////////////////////////////////////////////////////
    
    /// Serializes the JSON value into a string.
    string serialize() const;
    
    /// Assigns a value to the JSON value.
    /// @{
    void operator=(bool value);   
	void operator=(int value);
	void operator=(long value);
	void operator=(datetime value);
	void operator=(double value);
	void operator=(string value);
	void operator=(const JsonValue& value);
	/// @}
    
    /////////////////////////////////////////////////////////////////////////////
    /// @brief Finds or inserts a JSON value by key in a JSON object.
    ///
    /// If `type()` is `JSON_UNDEFINED`, makes it `JSON_OBJECT`.
    ///
    /// Then, if the JSON object contains `key`, returns a pointer to the JSON
    /// value associated with that key.
    ///
    /// Otherwise, inserts a value of type `JSON_UNDEFINED` associated with `key`
    /// into the JSON object and returns a pointer to the inserted value. The
    /// returned pointer may be assigned a value to by an assignment operator.
    ///
    /// @param A string key.
    /// @return Pointer to JSON value associated with `key`.
    /// @see `find()`
    ///
    /////////////////////////////////////////////////////////////////////////////
    JsonValue* operator[](string key);
    
    /////////////////////////////////////////////////////////////////////////////
    /// @brief Finds or inserts a JSON value by key in a JSON object.
    ///
    /// If `type()` is `JSON_UNDEFINED`, makes it `JSON_ARRAY`.
    ///
    /// Then, if `index` is less than `size()`, returns a pointer to the JSON
    /// value at `index`.
    ///
    /// Otherwise, tries to resize the JSON array by inserting JSON values of
    /// type `JSON_UNDEFINED` until `size() == (index + 1)`. If the resizing
    /// attempt fails, returns `NULL`. Otherwise, returns the last element in
    /// the array at `index`.
    ///
    /// @param An index.
    /// @return Pointer to JSON value at `index`, or `NULL` if resizing attempt
    ///         fails.
    /// @see `at()`
    ///
    /////////////////////////////////////////////////////////////////////////////
	JsonValue* operator[](int index);

    /////////////////////////////////////////////////////////////////////////////
    /// @brief Checks whether the JSON value is of type `JSON_UNDEFINED`.
    ///
    /// Effectively returns the result of `type() == JSON_UNDEFINED`.
    ///
    /// @return `true` if `JSON_UNDEFINED`, and `false` otherwise.
    ///
    /////////////////////////////////////////////////////////////////////////////
	bool operator!() const;

private:
    JsonValue(JsonValue* parent, JsonType type);

    void reset(JsonValue* parent = NULL, JsonType type = JSON_UNDEFINED);
    
    /// Grows `m_children` up by 1 element and returns a pointer to that element.
    JsonValue* append_child();
    
    /////////////////////////////////////////////////////////////////////////////
    /// Appends a `child` at the end of `m_children`.
    ///
    /// Let `p` be the result of invoking `append_child()`. Effectively invokes
    /// `p.set_value(child)` and returns `p`.
    ///
    /// @param child A child to be appended.
    ///
    /////////////////////////////////////////////////////////////////////////////
    JsonValue* append_child(const JsonValue& child);
    
    void serialize(string& js) const;
    bool deserialize(char& js[], int slen, int& i);
    bool parse_string(char& js[], int slen, int& i);
    
    string escape(string s) const;
    string unescape(string s);
    
    void set_bool(bool value);
    void set_int(long value);
	void set_double(double value);
	void set_string(string value);
	void set_value(const JsonValue& other);

    JsonValue* m_parent;
    JsonValue  m_children[];
	string     m_key;
	string     m_lkey;
	JsonType   m_type;
	bool       m_bv;
	long       m_iv;
	double     m_dv;
	int        m_dv_prec;
	string     m_sv;
};

/// Returns the string value of a `JsonType`, useful for debugging purposes.
string json_type_to_string(JsonType value_type)
{
    switch (value_type)
    {
        case JSON_UNDEFINED: return "JSON_UNDEFINED";
        case JSON_NULL:      return "JSON_NULL";
        case JSON_BOOL:      return "JSON_BOOL";
        case JSON_INTEGER:   return "JSON_INTEGER";
        case JSON_DOUBLE:    return "JSON_DOUBLE";
        case JSON_STRING:    return "JSON_STRING";
        case JSON_ARRAY:     return "JSON_ARRAY";
        case JSON_OBJECT:    return "JSON_OBJECT";
        default:             return NULL; // should never happen
    }
}

//===========================================================================
// --- JsonValue implementation ---
//===========================================================================
JsonValue JsonValue::deserialize(string json_str)
{
    JsonValue value;
    
    int i = 0;
    char js[];
    int slen = StringToCharArray(json_str, js, 0, WHOLE_ARRAY);

    value.deserialize(js, slen, i);

    return value;
}

JsonValue::JsonValue(JsonType type)
{
    reset(NULL, type);
}

JsonValue::JsonValue(const JsonValue& other)
{
    set_value(other);
}

JsonValue::JsonValue(JsonValue* parent, JsonType type)
{
    reset(parent, type);
}

JsonValue::~JsonValue()
{
}

void JsonValue::reset(JsonValue* parent, JsonType type)
{
    m_parent  = parent;
    m_type    = type;
    m_key     = "";
    m_bv      = false;
    m_iv      = 0;
    m_dv      = 0;
    m_dv_prec = 8;
    m_sv      = "";
}

void JsonValue::set_bool(bool value)
{
    m_type = JSON_BOOL;
    m_bv   = value;
    m_iv   = long(m_bv);
    m_dv   = double(m_bv);
}

void JsonValue::set_int(long value)
{
    m_type = JSON_INTEGER;
    m_iv   = value;
    m_dv   = double(m_iv);
    m_bv   = m_iv != 0;
}

void JsonValue::set_double(double value)
{
    m_type = JSON_DOUBLE;
    m_dv   = value;
    m_iv   = long(m_dv);
    m_bv   = m_iv != 0;
}

void JsonValue::set_string(string value)
{
    m_type = (value != NULL) ? JSON_STRING : JSON_NULL;
    m_sv   = value;
    m_iv   = StringToInteger(m_sv);
    m_dv   = StringToDouble(m_sv);
    m_bv   = value != NULL;
}

void JsonValue::set_value(const JsonValue& other)
{
	if (m_key == "")
    	m_key = other.m_key;

    m_type    = other.m_type;
    m_bv      = other.m_bv;
    m_iv      = other.m_iv;
    m_dv      = other.m_dv;
    m_dv_prec = other.m_dv_prec;
    m_sv      = other.m_sv;
    
    const int n = ArrayResize(m_children, ArraySize(other.m_children));
    
    for (int i = 0; i < n; i++)
    {
		m_children[i].m_parent = GetPointer(this);
        m_children[i] = other.m_children[i];
    }
}

JsonValue* JsonValue::append_child()
{
    const int n = size();
    
    ArrayResize(m_children, n + 1, 100);
    
    return GetPointer(m_children[n]);
}

JsonValue* JsonValue::append_child(const JsonValue& child)
{
    JsonValue* child_ptr = append_child();

    child_ptr.set_value(child);

    return child_ptr;
}

JsonValue* JsonValue::find(string key) const
{
    for (int i = size() - 1; i >= 0; --i)
    {
        if (m_children[i].m_key == key)
            return GetPointer(m_children[i]);
    }

    return NULL;
}

bool JsonValue::contains(string key) const
{
    return find(key).type() != JSON_UNDEFINED;
}

JsonValue* JsonValue::at(int index) const
{
    if (m_type == JSON_ARRAY && index >= 0 && index < size())
        return GetPointer(m_children[index]);

    return NULL;
}

int JsonValue::size() const
{
    return ArraySize(m_children);
}

JsonType JsonValue::type() const
{
    return m_type;
}

bool JsonValue::to_bool() const
{
    return m_bv;
}

long JsonValue::to_int() const
{
    return m_iv;
}

double JsonValue::to_double() const
{
    return m_dv;
}

string JsonValue::to_string() const
{
    return m_sv;
}

bool JsonValue::to_bool(bool& ok) const
{
    ok = type() == JSON_BOOL;

    return ok ? to_bool() : NULL;
}

long JsonValue::to_int(bool& ok) const
{
    ok = type() == JSON_INTEGER;
    
    return ok ? to_int() : NULL;
}

double JsonValue::to_double(bool& ok) const
{
    ok = type() == JSON_DOUBLE;
    
    return ok ? to_double() : NULL;
}

string JsonValue::to_string(bool& ok) const
{
    ok = type() == JSON_STRING;

    return ok ? to_string() : NULL;
}

string JsonValue::serialize() const
{
    string js;
    
    serialize(js);

    return js;
}

void JsonValue::operator=(bool value)
{
    set_bool(value);
}

void JsonValue::operator=(int value)
{
    set_int(long(value));
}

void JsonValue::operator=(long value)
{
    set_int(value);
}

void JsonValue::operator=(datetime value)
{
	set_int(long(value));
}

void JsonValue::operator=(double value)
{
    set_double(value);
}

void JsonValue::operator=(string value)
{
    set_string(value);
}

void JsonValue::operator=(const JsonValue& value)
{
    set_value(value);
}

JsonValue* JsonValue::operator[](string key)
{
    if (m_type == JSON_UNDEFINED)
        m_type = JSON_OBJECT;
    
    JsonValue* child = find(key);
    
    if (!child)
    {
        child = append_child();
        child.m_key = key;
    }

    return child;
}

JsonValue* JsonValue::operator[](int index)
{
    if (m_type == JSON_UNDEFINED)
        m_type = JSON_ARRAY;

	while (index >= size())
	{
	    JsonValue* child = append_child();
	    
	    if (CheckPointer(child) == POINTER_INVALID)
	        return NULL;
	}

	return GetPointer(m_children[index]);
}

bool JsonValue::operator!() const
{
    return type() == JSON_UNDEFINED;
}

void JsonValue::serialize(string& js) const
{
    if (m_type == JSON_UNDEFINED)
	    return;
	    
	const int n = size();
	
	switch (m_type)
	{
    	case JSON_NULL:    js += "null";                          break;
    	case JSON_BOOL:    js += (m_bv ? "true" : "false");       break;
    	case JSON_INTEGER: js += IntegerToString(m_iv);           break;
    	case JSON_DOUBLE:  js += DoubleToString(m_dv, m_dv_prec); break;
    	
    	case JSON_STRING:
    	{
    	    const string ss = escape(m_sv);

    	    if (StringLen(ss) > 0)
    	        js += StringFormat("\"%s\"", ss);
    	    else
    	        js += "null";
    	}
    	break;
    	
    	case JSON_ARRAY:
    	{
    	    js += "[";
    	    
    	    for (int i = 0, last_serialized_i = -1; i < n; i++)
			{
				string child_js = "";
    	        
				m_children[i].serialize(child_js);

				if (child_js == "")
					continue;
				
				//==========================================================================
				// Comma is appended to the current child, provided that another child was
				// successfully serialized before it, that is, that the current child is not
				// the first serialized child. This is done this way because we don't know
				// if the next child will result in a valid serialization. For instance,
				// consider the following array:
				//
				// [JSON_UNDEFINED, 10, JSON_UNDEFINED]
				//
				// The resulting string must be "[10]", which is only possible by ignoring
				// the previous and next JSON_UNDEFINED children.
				//==========================================================================
				if (last_serialized_i != -1)
					js += ",";

				js += child_js;

				last_serialized_i = i;
			}

    	    js += "]"; 
    	}
    	break;
    	
    	case JSON_OBJECT:
    	{
    	    js += "{";

    	    for (int i = 0, last_serialized_i = -1; i < n; i++)
			{
				string child_js = "";
    	        
				m_children[i].serialize(child_js);
				
				if (child_js == "")
					continue;

				if (last_serialized_i != -1)
					js += ",";

				js += StringFormat("\"%s\":%s",  m_children[i].m_key, child_js);

				last_serialized_i = i;
			}
    	    
    	    js += "}";
    	}
    	break;
	}
}

bool JsonValue::deserialize(char& js[], int slen, int& i)
{
	for (; i < slen; i++)
	{
		const char c = js[i];

		if (c == 0)
		    break;

		switch (c)
		{
		    // Ignored characters.
		    case '\t':
		    case '\r':
		    case '\n':
		    case ' ':
			    break;

            // Beginning of JSON array.
    		case '[':
    		{
    			if (m_type != JSON_UNDEFINED)
    			{
    			    Print(m_key + " " + string(__LINE__));
    			    return false;
    			}

    			// Skip '['.
    			i++;

    			m_type = JSON_ARRAY;
    			JsonValue value(GetPointer(this), JSON_UNDEFINED);
    			
    			while (value.deserialize(js, slen, i))
    			{
    			    switch (value.m_type)
    			    {
    			        case JSON_UNDEFINED:
    			            break;
    			        
    			        case JSON_INTEGER:
    			        case JSON_DOUBLE:
    			        case JSON_ARRAY:
    			            i++;
    			            // fallthrough.

    			        default:
    			            append_child(value);
    			    }
                    
    				if (js[i] == ']')
    				    break;

    				i++;
    				
    				if (i >= slen)
    				{
    				    Print(m_key + " " + string(__LINE__));
    				    return false;
    				}

    				value.reset(GetPointer(this), JSON_UNDEFINED);
    			}

    			return js[i] == ']' || js[i] == 0;
    		}
    		break;
    		
    		// End of JSON array.
    		case ']':
    		    if (!m_parent)
    		        return false;

    		    return m_parent.type() == JSON_ARRAY;
    
            // Value of JSON object.
    		case ':':
    		{
    			if (m_lkey == "")
    			{
    			    Print(m_key + " " + string(__LINE__));
    			    return false;
    			}
    			
    			// Skip ':'.
    			i++;

    			JsonValue* child = append_child();
    			child.m_key      = m_lkey;
    			m_lkey           = "";

    			if (!child.deserialize(js, slen, i))
    			{
    			    Print(m_key + " " + string(__LINE__));
    			    return false;
    			}

    			break;
    		}
    		
    		// End of JSON element.
    		case ',':
    		{
    			if (!m_parent && m_type != JSON_OBJECT)
    			{
    			    Print(m_key + " " + string(__LINE__));
    			    return false;
    			}
    			
    			if (m_parent)
    			{
    				if (m_parent.type() != JSON_ARRAY && m_parent.type() != JSON_OBJECT)
    				{
    				    Print(m_key + " " + string(__LINE__));
    				    return false;
    				}
    				
    				if (m_parent.type() == JSON_ARRAY && m_type == JSON_UNDEFINED)
    				    return true;
    			}
    	    }
    		break;
    
            // Beginning of JSON object.
    		case '{':
    		{
    			if (m_type != JSON_UNDEFINED)
    			{
    			    Print(m_key + " " + string(__LINE__));
    			    return false;
    			}
    			
    			// Skip '{'.
    			i++;
    			
    			m_type = JSON_OBJECT;
    			
    			if (!deserialize(js, slen, i))
    			{
    			    Print(m_key + " " + string(__LINE__));
    			    return false;
    			}
    			
    			return js[i] == '}' || js[i] == 0;
    	    }
    		break;

    		// End of JSON object.
    		case '}':
    		    return m_type == JSON_OBJECT;
    
            // JSON boolean (true, false, True, False).
    		case 't':
    		case 'f':
    		case 'T':
    		case 'F':
    		{
    			if (m_type != JSON_UNDEFINED)
    			{
    			    Print(m_key + " " + string(__LINE__));
    			    return false;
    			}

    			m_type = JSON_BOOL;
    			
    			if ((i + 3) < slen)
    			{
    			    if (StringCompare(CharArrayToString(js, i, 4), "true", false) == 0)
    			    {
    			        m_bv = true;
    			        i += 3;
    			        
    			        return true;
    			    }
    			}

    			if ((i + 4) < slen)
    			{
    			    if (StringCompare(CharArrayToString(js, i, 5), "false", false) == 0)
    			    {
    			        m_bv = false;
    			        i += 4;
    			        
    			        return true;
    			    }
    			}
    			
    			Print(m_key + " " + string(__LINE__));
    			return false;
    	    }
    	    break;

            // JSON null (null, Null).
    		case 'n':
    		case 'N':
    		{
    			if (m_type != JSON_UNDEFINED)
    			{
    			    Print(m_key + " " + string(__LINE__));
    			    return false;
    			}
    			
    			m_type = JSON_NULL;
    			
    			if ((i + 3) < slen && StringCompare(CharArrayToString(js, i, 4), "null", false) == 0)
    			{
    			    i += 3;
    			    return true;
    			}
    			
    			Print(m_key + " " + string(__LINE__));
    			return false;
    		}
    		break;
    
            // JSON number.
    		case '0': case '1': case '2': case '3': case '4': case '5': case '6': case '7': case '8': case '9':
    		case '-': case '+': case '.':
    		{
    			if (m_type != JSON_UNDEFINED)
    			{
    			    Print(m_key + " " + string(__LINE__));
    			    return false;
    			}
    			
    			bool is_double = false;
    			int start_i = i;

    			while (js[i] != 0 && i < slen)
    			{
    			    i++;
    			    
    			    if (StringFind("0123456789+-.eE", CharArrayToString(js, i, 1)) < 0)
    			        break;

    			    if (!is_double)
    			        is_double = (js[i] == '.' || js[i] == 'e' || js[i] == 'E');
    			}
    			
    			m_sv = CharArrayToString(js, start_i, i - start_i);

    			if (is_double)
    			    set_double(StringToDouble(m_sv));
                else
                    set_int(StringToInteger(m_sv));

    			i--;
    			
    			return true;
    		}
    		break;
    		
    		// JSON string.
    		case '\"':
    		{
    		    // Check if JSON string is a value or a key in a JSON object.
    			if (m_type == JSON_OBJECT)
    			{
    			    // Skip quotation mark (").
    				i++;

    				int start_i = i;
    				
    				if (!parse_string(js, slen, i))
    				{
    				    Print(m_key + " " + string(__LINE__));
    				    return false;
    				}

                    m_lkey = CharArrayToString(js, start_i, i - start_i);
    			}
    			else
    			{
    				if (m_type != JSON_UNDEFINED)
    				{
    				    Print(m_key + " " + string(__LINE__));
    				    return false;
    				}

    				// Skip quotation mark (").
    				i++;
    				
    				m_type = JSON_STRING;

    				int start_i = i;

    				if (!parse_string(js, slen, i))
    				{
    				    Print(m_key + " " + string(__LINE__));
    				    return false;
    				}

                    const string sv = CharArrayToString(js, start_i, i - start_i);

                    set_string(unescape(sv));

    				return true;
    			}
    		}
    		break;
		}
	}

	return true;
}

bool JsonValue::parse_string(char& js[], int slen, int& i)
{
	for (; js[i] != 0 && i < slen; i++)
	{
		char c = js[i];

		if (c == '\"')
		    break;

		if (c == '\\' && (i + 1) < slen)
		{
			i++;
			
			c = js[i];
			
			switch (c)
			{
			    case '/': case '\\': case '\"': case 'b': case 'f': case 'r': case 'n': case 't':
			        break;

                // Unicode string ("\uXXXX").
			    case 'u': 
    			{
    				i++;
    				
    				for (int j = 0; j < 4 && i < slen && js[i] != 0; j++, i++)
    				{
    					if (!((js[i] >= '0' && js[i] <= '9') || (js[i] >= 'A' && js[i] <= 'F') || (js[i]>='a' && js[i]<='f')))
    					{
    					    Print(m_key + " " + CharToString(js[i]) + " " + string(__LINE__));
    					    return false;
    					}
    				}
    				
    				i--;
    				
    				break;
    			}
    			
			    default:
			        break;
			}
		}
	}

	return true;
}

string JsonValue::escape(string s) const
{
	ushort in_arr[], out_arr[];
	const int n = StringToShortArray(s, in_arr);

	if (ArrayResize(out_arr, 2 * n) != (2 * n))
	    return NULL;

// MQL doesn't support the escaped characters '\b' and '\f', which JSON
// supports. So we have to use their numeric code instead.
#define ESCAPED_B 8  // '\b'
#define ESCAPED_F 12 // '\f'
	
	int j = 0;
	
	for (int i = 0; i < n; i++)
	{
		switch (in_arr[i])
		{
    		case '\\':      out_arr[j++] = '\\'; out_arr[j++] = '\\'; break;
    		case '"':       out_arr[j++] = '\\'; out_arr[j++] = '"';  break;
    		case '/':       out_arr[j++] = '\\'; out_arr[j++] = '/';  break;
    		case ESCAPED_B: out_arr[j++] = '\\'; out_arr[j++] = 'b';  break;
    		case ESCAPED_F: out_arr[j++] = '\\'; out_arr[j++] = 'f';  break;
    		case '\n':      out_arr[j++] = '\\'; out_arr[j++] = 'n';  break;
    		case '\r':      out_arr[j++] = '\\'; out_arr[j++] = 'r';  break;
    		case '\t':      out_arr[j++] = '\\'; out_arr[j++] = 't';  break;
    		default:
    		    out_arr[j++] = in_arr[i];
    		    break;
		}
	}

#undef ESCAPED_B
#undef ESCAPED_F

	return ShortArrayToString(out_arr, 0, j);
}

string JsonValue::unescape(string s)
{
	ushort in_arr[], out_arr[];

	int n = StringToShortArray(s, in_arr);
	
	if (ArrayResize(out_arr, n) != n)
	    return NULL;
	
	// MQL doesn't support the escaped characters '\b' and '\f', which JSON
	// supports. So we have to use their numeric code instead.
	const ushort escaped_b = 8;  // '\b'
	const ushort escaped_f = 12; // '\f'
	
	int j = 0, i = 0;

	while (i < n)
	{
		ushort c = in_arr[i];
		
		if (c == '\\' && i < (n - 1))
		{
			switch (in_arr[i + 1])
			{
    			case '\\': c = '\\';      i++; break;
    			case '"':  c = '"';       i++; break;
    			case '/':  c = '/';       i++; break;
    			case 'b':  c = escaped_b; i++; break;
    			case 'f':  c = escaped_f; i++; break;
    			case 'n':  c = '\n';      i++; break;
    			case 'r':  c = '\r';      i++; break;
    			case 't':  c = '\t';      i++; break;
    			case 'u':  // \uXXXX
    			{
    				i += 2;
    				
    				ushort k = 0;
    				
    				for (int jj = 0; jj < 4 && i < n; jj++, i++)
    				{
    					c = in_arr[i];

    					ushort h = 0;
    					
    					if      (c >= '0' && c <= '9') h = c - '0';
    					else if (c >= 'A' && c <= 'F') h = (c - 'A') + 0xA;
    					else if (c >= 'a' && c <= 'f') h = (c - 'a') + 0xA;
    					else break;
    					
    					k += h * ushort(pow(16, (3 - jj)));
    				}

    				i--;
    				c = k;

    				break;
    			}
			}
		}
		
		out_arr[j] = c;
		
		j++;
		i++;
	}
	
	return ShortArrayToString(out_arr, 0, j);
}