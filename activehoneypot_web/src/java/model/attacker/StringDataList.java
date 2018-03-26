package model.attacker;

import dbUtils.*;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;

public class StringDataList {

    public String dbError = "";
    private ArrayList<StringData> recordList = new ArrayList();

    // Default constructor just leaves the 2 data members initialized as above
    public StringDataList() {
    }

    // overloaded constructor populates the list (and possibly the dbError)
    public StringDataList(String attackerNameStartsWith, DbConn dbc) {

        StringData sd = new StringData();

        System.out.println("Searching for champions that start with " + attackerNameStartsWith);

        try {

            String sql = "SELECT attackerID, ip_address, username, password, timeOfDayAccessed, metadata, logFile FROM attacker "
                    + " WHERE logFile LIKE ? ORDER BY logFile";

            PreparedStatement stmt = dbc.getConn().prepareStatement(sql);
            stmt.setString(1, attackerNameStartsWith + "%");
            ResultSet results = stmt.executeQuery();

            while (results.next()) {
                try {
                    sd = new StringData();
                    sd.attackerID = FormatUtils.formatInteger(results.getObject("attackerID"));
                    sd.ip_address = FormatUtils.formatString(results.getObject("ip_address"));
                    sd.username = FormatUtils.formatString(results.getObject("username"));
                    sd.password = FormatUtils.formatString(results.getObject("password"));
                    sd.dateAccessed = FormatUtils.formatDate(results.getObject("timeOfDayAccessed"));
                    sd.timeOfDayAccessed = FormatUtils.formatTime(results.getObject("timeOfDayAccessed"));
                    sd.metadata = FormatUtils.formatString(results.getObject("metadata"));
                    sd.logFile = FormatUtils.formatString(results.getObject("logFile"));
                    this.recordList.add(sd);
                } catch (Exception e) {
                    sd.errorMsg = "Record Level Error in model.Attacker.StringDataList Constructor: " + e.getMessage();
                    this.recordList.add(sd);
                }
            } // while
        } catch (Exception e) {
            this.dbError = "List Level Error in model.Attacker.StringDataList Constructor: " + e.getMessage();
        }
    } // method

} // class
