<%@page contentType="application/json; charset=UTF-8" pageEncoding="UTF-8"%> 

<%@page language="java" import="dbUtils.*" %>
<%@page language="java" import="model.attacker.*" %>
<%@page language="java" import="java.util.ArrayList" %>

<%@page language="java" import="com.google.gson.*" %>

<%

    StringDataList list = new StringDataList();

    DbConn dbc = new DbConn();
    list.dbError = dbc.getErr(); // returns "" if connection is good, else db error msg.

    if (list.dbError.length() == 0) { // got open connection 

        String attackerNameStartsWith = request.getParameter("q");
        if (attackerNameStartsWith == null) {
            attackerNameStartsWith = "";
        }

            System.out.println("jsp page ready to search for attacker with " + attackerNameStartsWith);
            list = new StringDataList(attackerNameStartsWith, dbc, "country");
    } 

    // PREVENT DB connection leaks:
    dbc.close(); 

    Gson gson = new Gson();
    out.print(gson.toJson(list).trim()); 
%>