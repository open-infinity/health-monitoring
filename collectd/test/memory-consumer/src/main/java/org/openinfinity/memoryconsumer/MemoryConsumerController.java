package org.openinfinity.memoryconsumer;

import java.util.ArrayList;
import java.util.List;

import org.springframework.stereotype.Controller;
import org.springframework.ui.ModelMap;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

@Controller
@RequestMapping("/consume")
public class MemoryConsumerController {
    
    //10 pow(15)=
    static final long BIG_RAM_IN_BYTES = 1000000000000000L;
    
    //10 pow(7)
    static final int STEP_IN_BYTES = 200000000;
    
	@RequestMapping(value="/{consumeAction}", method = RequestMethod.GET)
	public String consume(@PathVariable String consumeAction, ModelMap model) throws InterruptedException {

	    if (consumeAction.equals("all")){
	        consume(BIG_RAM_IN_BYTES);
            }
	    return null;
	}
	
	@RequestMapping(value="/{consumeAction}/bytes/{bytes}", method = RequestMethod.GET)
    public String consume(@PathVariable String consumeAction, @PathVariable String bytes, ModelMap model) throws InterruptedException {

        if (consumeAction.equals("amount")){
            consume(Long.parseLong(bytes));
            }
        model.addAttribute("bytes", bytes);
        return "amount";
    }
	
	void consume(long limit) throws InterruptedException{
	    List<byte[]> heapChunkList = new ArrayList(); 
	    for (int i = 0; i < limit/STEP_IN_BYTES; i++){
            heapChunkList.add(new byte[STEP_IN_BYTES]);
        }    
	}
}