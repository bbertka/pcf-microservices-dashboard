package com.example;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestMapping;

/**
 * @author bbertka
 *
 */
@Controller
public class DashboardController {
	
	/*
	 * Returns the home page for the Dashboard
	 * These will be replaced with functions that return JSON for the services
	 * Currently these are used to pull pre-made iframes of the microservices,
	 * however the data models already exist, just need to implement the javascript here to pull
	 */
	
	@RequestMapping("/")
	public String dashboard(Model model){
		model.addAttribute("TIMELINE_API", "//"+System.getenv("CONSUMER_FQDN")+"/metrics/timeline");
		model.addAttribute("BUBBLES_API", "//"+System.getenv("CONSUMER_FQDN")+"/metrics/field-value-counters/hashtags");
		model.addAttribute("PROFILES_API", "//"+System.getenv("PROFILES_FQDN")+"/metrics/profiles");
		model.addAttribute("NEWS_API", "//"+System.getenv("NEWS_FQDN")+"/autosearch");
		model.addAttribute("SENTIMENT_API", "//"+System.getenv("CONSUMER_FQDN")+"/metrics/field-value-counters/sentiment");
		
		



		return "dashboard";
	}
	
}

