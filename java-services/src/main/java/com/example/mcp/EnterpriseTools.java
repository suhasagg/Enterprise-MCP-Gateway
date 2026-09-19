package com.example.mcp;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Value;

@Service
public class EnterpriseTools {
 private final String mode;
 private final Map<String,Ticket> tickets=new ConcurrentHashMap<>();
 public EnterpriseTools(@Value("${SERVICE_MODE:crm}") String mode){this.mode=mode;}

 private void require(String expected){
  if(!mode.equals(expected)) throw new IllegalStateException("tool unavailable on "+mode+" service");
 }

 @Tool(description="Get customer record by id. Read-only.")
 public Customer get_customer(String customer_id){
  require("crm");
  if(customer_id.equals("CUST-1001")) return new Customer(customer_id,"Contoso","enterprise","active");
  return new Customer(customer_id,"unknown","unknown","not_found");
 }

 @Tool(description="Create support ticket.")
 public Ticket create_ticket(String customer_id,String title,String description,String priority){
  require("crm");
  String id="T-"+UUID.randomUUID().toString().substring(0,8);
  var t=new Ticket(id,customer_id,title,priority,"open",Instant.now().toString());
  tickets.put(id,t); return t;
 }

 @Tool(description="Get deployment state. Read-only.")
 public Deployment get_deployment(String service,String environment){
  require("ops");
  return new Deployment(service,environment,service+":v42",4,4,"healthy");
 }

 @Tool(description="Restart a service. Gateway is responsible for policy and approval.")
 public ActionResult restart_service(String service,String environment,String reason){
  require("ops");
  return new ActionResult(true,"restart",service,environment,
    "restart accepted: "+reason,"act-"+UUID.randomUUID());
 }

 public record Customer(String id,String name,String tier,String status){}
 public record Ticket(String id,String customerId,String title,String priority,String status,String createdAt){}
 public record Deployment(String service,String environment,String image,int desired,int ready,String status){}
 public record ActionResult(boolean success,String action,String service,String environment,String message,String actionId){}
}