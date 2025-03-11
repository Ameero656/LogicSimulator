#include <vector>
#include <string>
#include <fstream>
#include <iostream>
#include <optional>
#include <stdexcept>
#include "json.hpp"

using namespace std;
using json = nlohmann::json;

struct Port {
    optional<int> node;  // if null in json, becomes nullopt
    int port;
};

struct Connection {
    Port source;
    Port sink;
};

class Blueprint {
public:
    vector<string> node_list;
    vector<Connection> connections;
    int num_inputs;
    int num_outputs;
    vector<string> input_labels;
    vector<string> output_labels;
    string id;

    void populate_from_json(const json& j) {
        node_list = j.at("node_list").get<vector<string>>();
        
        connections.clear();
        for (const auto& conn_json : j.at("connections")) {
            Connection conn;
            if (conn_json.at("source").at("node").is_null())
                conn.source.node = nullopt;
            else
                conn.source.node = conn_json.at("source").at("node").get<int>();
            conn.source.port = conn_json.at("source").at("port").get<int>();
            
            if (conn_json.at("sink").at("node").is_null())
                conn.sink.node = nullopt;
            else
                conn.sink.node = conn_json.at("sink").at("node").get<int>();
            conn.sink.port = conn_json.at("sink").at("port").get<int>();

            connections.push_back(conn);
        }
        
        num_inputs = j.at("num_inputs").get<int>();
        num_outputs = j.at("num_outputs").get<int>();
        input_labels = j.at("input_labels").get<vector<string>>();
        output_labels = j.at("output_labels").get<vector<string>>();
        id = j.at("id").get<string>();
    }

    static Blueprint from_json_file(const string& file_name) {
        ifstream file(file_name);
        if (!file)
            throw runtime_error("Cannot open file: " + file_name);
        json j;
        file >> j;
        Blueprint bp;
        bp.populate_from_json(j);
        return bp;
    }
};


class LogicEngine {

    bool validateBlueprint(Blueprint& self) {}
    vector<bool> evaluateBlueprint(Blueprint& self) {}

    //TODO: implement these two functions

};



int main() {
    
}