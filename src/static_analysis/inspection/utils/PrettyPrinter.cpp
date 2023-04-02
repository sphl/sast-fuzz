#include "PrettyPrinter.h"

#include "rapidjson/stringbuffer.h"
#include "rapidjson/writer.h"

using namespace std;
using namespace rapidjson;

string PrettyPrinter::convertToJSON(vector<FuncInfo> &funcInfos) {
    StringBuffer sb;
    Writer<StringBuffer> writer(sb);

    writer.StartObject();
    writer.Key("functions");
    writer.StartArray();
    for (auto &funcInfo : funcInfos) {
        writer.StartObject();
        writer.Key("name");
        writer.String(funcInfo.getName().c_str());

        writer.Key("location");
        writer.StartObject();
        writer.Key("filename");
        writer.String(funcInfo.getFilename().c_str());

        writer.Key("line");
        writer.StartObject();
        writer.Key("start");
        writer.Uint64(funcInfo.getLineRange().first);

        writer.Key("end");
        writer.Uint64(funcInfo.getLineRange().second);
        writer.EndObject();  // function -- line

        writer.Key("reachable_from_main");
        writer.Bool(funcInfo.isReachableFromMain());
        writer.EndObject();  // function -- location

        writer.Key("stats");
        writer.StartObject();
        writer.Key("LoC");
        writer.Uint(funcInfo.getLineNumbers().size());
        writer.EndObject();  // function -- stats
        writer.EndObject();

        writer.Key("basic_blocks");
        writer.StartArray();
        for (auto &blockInfo : funcInfo.getBlockInfos()) {
            writer.StartObject();
            writer.Key("id");
            writer.Uint64(blockInfo.getId());

            writer.Key("location");
            writer.StartObject();
            writer.Key("line");
            writer.StartObject();
            writer.Key("start");
            writer.Uint64(blockInfo.getLineRange().first);

            writer.Key("end");
            writer.Uint64(blockInfo.getLineRange().second);
            writer.EndObject();  // BB -- line

            writer.EndObject();  // BB -- location

            writer.Key("stats");
            writer.StartObject();
            writer.Key("LoC");
            writer.Uint(blockInfo.getLineNumbers().size());
            writer.EndObject();  // BB -- stats
            writer.EndObject();
        }
        writer.EndArray();  // BBs
    }
    writer.EndArray();  // functions
    writer.EndObject();

    return sb.GetString();
}