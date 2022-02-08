<%@ page contentType="text/html;charset=UTF-8" language="java" %>

<%@ page import="java.util.Enumeration" %>
<%@ page import="java.util.HashMap" %>
<%@ page import="java.util.Map" %>

<%@ include file="security.jsp" %>

<html>
<head>
    <title>Unsigned Data Fields</title>
    <link rel="stylesheet" type="text/css" href="payment.css">
</head>
<body>
<form id="payment_confirmation" action="https://testsecureacceptance.cybersource.com/silent/pay" method="post">
	<%
	    request.setCharacterEncoding("UTF-8");
		HashMap params = new HashMap();
	    Enumeration paramsEnum = request.getParameterNames();
	    while (paramsEnum.hasMoreElements()) {
	        String paramName = (String) paramsEnum.nextElement();
	        String paramValue = request.getParameter(paramName);
	        params.put(paramName, paramValue);
	    }
	%>
	<fieldset id="confirmation">
	    <legend>Signed Data Fields</legend>
	These fields have been signed on your server, and a signature has been generated.  This will <br> detect tampering with these values as they pass through the consumers browser to the SASOP endpoint.<BR></BR>
	    <div>
	        <%
	            Iterator paramsIterator = params.entrySet().iterator();
	            while (paramsIterator.hasNext()) {
	                Map.Entry param = (Map.Entry) paramsIterator.next();
	        %>
	        <div>
	            <span class="fieldName"><%=param.getKey()%>:</span><span class="fieldValue"><%=param.getValue()%></span>
	        </div>
	        <%
	            }
	        %>
	    </div>
	</fieldset>
		<%
	    	paramsIterator = params.entrySet().iterator();
	    	while (paramsIterator.hasNext()) {
	        	Map.Entry param = (Map.Entry) paramsIterator.next();
	        	out.print("<input type=\"hidden\" id=\"" + param.getKey() + "\" name=\"" + param.getKey() + "\" value=\"" + param.getValue() + "\">\n");
	    	}
	    	out.print("<input type=\"hidden\" id=\"signature\" name=\"signature\" value=\"" + sign(params) + "\">\n");
		%>
	    <fieldset>
	        <legend>Unsigned Data Fields</legend>  
	        Card data fields are posted directly to CyberSource, together with the fields above.  These field <br>
	        names will need to be included in the unsigned_field_names.
	        <BR></BR>
	        <div id="UnsignedDataSection" class="section">
	        <span>card_type:</span><input type="text" name="card_type"><br>
	        <span>card_number:</span><input type="text" name="card_number"><br>
	        <span>card_expiry_date:</span><input type="text" name="card_expiry_date"><br>
		</div>
	    </fieldset>
	  <input type="submit" id="submit" value="Confirm">
</form>
<script type="text/javascript" src="jquery-1.7.min.js"></script>
  <script type="text/javascript" src="payment_form.js"></script>
</body>
</html>
