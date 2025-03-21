package com.example.serviceA.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController

public class ServiceARestController {
    @GetMapping("/helloworld")
    public String helloWorld(){
        return "Hello world from service A";
    }
}
