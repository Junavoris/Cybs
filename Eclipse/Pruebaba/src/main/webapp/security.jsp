<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ page import="javax.xml.bind.DatatypeConverter" %>
<%@ page import="javax.crypto.Mac" %>
<%@ page import="javax.crypto.spec.SecretKeySpec" %>
<%@ page import="java.security.InvalidKeyException" %>
<%@ page import="java.security.NoSuchAlgorithmException" %>
<%@ page import="java.io.UnsupportedEncodingException" %>
<%@ page import="java.util.ArrayList" %>
<%@ page import="java.util.Iterator" %>
<%@ page import="java.util.*"%> 

<%! private static final String HMAC_SHA256 = "HmacSHA256";
    private static final String SECRET_KEY = "a49ea5df0066437fa78c792d175fb4c56068969fcb844018b7a38bbda287baca3be03231123442e2a8399f682cfc195e8812e558bb134a6d84e1d2a372d24846a5f94e3fa3494c26a2014e6c8827a6e6bb23fd9aeabe428fb2d6f2d779dd37c103d45af7263e43f2851f7232675cea67cb50820cef1d4be69fabf395adcfd92a";

    private String sign(HashMap params) throws InvalidKeyException, NoSuchAlgorithmException, UnsupportedEncodingException {
        return sign(buildDataToSign(params), SECRET_KEY);
    }

    private String sign(String data, String secretKey) throws InvalidKeyException, NoSuchAlgorithmException, UnsupportedEncodingException {
        SecretKeySpec secretKeySpec = new SecretKeySpec(secretKey.getBytes(), HMAC_SHA256);
        Mac mac = Mac.getInstance(HMAC_SHA256);
        mac.init(secretKeySpec);
        byte[] rawHmac = mac.doFinal(data.getBytes("UTF-8"));
        return DatatypeConverter.printBase64Binary(rawHmac).replace("\n", "");
    }

    private String buildDataToSign(HashMap params) {
        String[] signedFieldNames = String.valueOf(params.get("signed_field_names")).split(",");
        ArrayList<String> dataToSign = new ArrayList<String>();
        for (String signedFieldName : signedFieldNames) {
            dataToSign.add(signedFieldName + "=" + String.valueOf(params.get(signedFieldName)));
        }
        return commaSeparate(dataToSign);
    }

    private String commaSeparate(ArrayList<String> dataToSign) {
        StringBuilder csv = new StringBuilder();
        for (Iterator<String> it = dataToSign.iterator(); it.hasNext(); ) {
            csv.append(it.next());
            if (it.hasNext()) {
                csv.append(",");
            }
        }
        return csv.toString();
    }
%>
