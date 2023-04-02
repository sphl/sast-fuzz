#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"

#include "PrettyPrinter.h"

using namespace std;
using namespace rapidjson;

string PrettyPrinter::convertToJSON(vector<FuncInfo> funcInfos) {
    StringBuffer sb;
    Writer<StringBuffer> writer(sb);

    writer.StartObject();
    writer.Key("functions");
    writer.StartArray();
    for (auto info : funcInfos) {
        writer.StartObject();
        writer.Key("name");
        writer.String(info.getName().c_str());

        writer.Key("location");
        writer.StartObject();
        writer.Key("filename");
        writer.String(info.getFilename().c_str());

        writer.Key("line");
        writer.StartObject();
        writer.Key("start");
        writer.Uint(info.getLineRange().first);

        writer.Key("end");
        writer.Uint(info.getLineRange().second);
        writer.EndObject(); // line

        writer.Key("reachable_from_main");
        writer.Bool(info.isReachableFromMain());
        writer.EndObject(); // location

        writer.Key("stats");
        writer.StartObject();
        writer.Key("LoC");
        writer.Uint(info.getLineNumbers().size());
        writer.EndObject(); // stats
        writer.EndObject();
    }
    writer.EndArray(); // functions
    writer.EndObject();

    return sb.GetString();
}
