
//package com.tutorialspoint.xml;

import java.io.*;
import java.io.File;
import java.util.ArrayList;
import java.util.HashMap;

import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.DocumentBuilder;
import org.w3c.dom.*;

public class Parser {
	
	public static void main(String[] args) {

		try {
			File inputFile = new File("Main-3.xml");

			DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
			DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();

			// Parses xml to a Document Object Model (DOM) file
			Document doc = dBuilder.parse(inputFile);

			doc.getDocumentElement().normalize();
			System.out.println("Root element: " + doc.getDocumentElement().getNodeName());
			NodeList nList = doc.getElementsByTagName("Document");
			NodeList nodes = nList.item(0).getChildNodes();

			// Go into SWBlocks
			NodeList SWBlock = nodes.item(5).getChildNodes();

			// Go into Object List
			NodeList objList = SWBlock.item(3).getChildNodes();

			// Go into Compile Unit
			NodeList compUnit = objList.item(3).getChildNodes();

			// Go into Attribute List
			NodeList attList = compUnit.item(1).getChildNodes();

			// Go into Network source
			NodeList networkSrc = attList.item(1).getChildNodes();

			// Go into FlgNet
			NodeList FlgNet = networkSrc.item(0).getChildNodes();

			// Go into Parts
			NodeList parts = FlgNet.item(1).getChildNodes();

			// Get each part
			HashMap<Integer, Part> p = new HashMap<Integer, Part>();
			PrintWriter pw = new PrintWriter("output.txt"); 
			for (int temp = 0; temp < parts.getLength(); temp++) {
				if (parts.item(temp).getNodeType() == Node.ELEMENT_NODE) {

					Element eElement = (Element) parts.item(temp);
					String name = "Special";
					String id = "";
					String type = "";
					int cardinality = -1;
					// For regular parts
					if (eElement.getNodeName() == "Access") {
						Element names = (Element) parts.item(temp).getChildNodes().item(1).getChildNodes().item(1);
						name = names.getAttribute("Name");
						type = eElement.getAttribute("Scope");
					}
					// For special parts
					else {
						type = eElement.getAttribute("Name");
						
						if (eElement != null && eElement.getChildNodes().getLength() > 1) {
							Element description = (Element) eElement.getChildNodes().item(1);
							name = description.getAttribute("Name");
							 
							if (name.equals("Card")) {
								cardinality = Integer.parseInt(description.getChildNodes().item(0).getNodeValue());
							}
						}

					}
					id = eElement.getAttribute("UId");
					int iD = Integer.parseInt(id);
					Part part = new Part(type, iD, name, cardinality);

					pw.println(part);
					p.put(iD, part);
				}
			}

			// Go into Wires
			NodeList wires = FlgNet.item(3).getChildNodes();
			
			ArrayList<Wire> w = new ArrayList<Wire>();
			
			for (int temp = 0; temp < wires.getLength(); temp++) {
				if (parts.item(temp).getNodeType() == Node.ELEMENT_NODE) {
					Element eElement = (Element) wires.item(temp);
					String id = "";
					String name = "IdentCon";
					id = eElement.getAttribute("UId");
					int iD = Integer.parseInt(id);
					Wire wire = new Wire(iD);
					
					for (int i = 1; i < eElement.getChildNodes().getLength(); i += 2) {
						Element partConn = (Element) eElement.getChildNodes().item(i);
						int partId = 0;
						if (!partConn.getAttribute("Name").equals("")) {
							partId = Integer.parseInt(partConn.getAttribute("UId"));
							name = partConn.getAttribute("Name");
						}
						
						wire.addConn(partId, name);
					}
					
					pw.println(wire);
					w.add(wire);
				}
			}
			
			pw.close(); 
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
}
