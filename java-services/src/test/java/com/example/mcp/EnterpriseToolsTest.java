package com.example.mcp;
import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
class EnterpriseToolsTest {
 @Test void crmCustomer(){
  var t=new EnterpriseTools("crm");
  assertEquals("Contoso",t.get_customer("CUST-1001").name());
 }
 @Test void opsDeployment(){
  var t=new EnterpriseTools("ops");
  assertEquals("healthy",t.get_deployment("checkout","production").status());
 }
}