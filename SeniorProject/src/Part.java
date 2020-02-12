
public class Part {
	private String type;
	private int id;
	private String name;
	private int cardinality;
	
	public Part(String type, int id, String name, int cardinality) {
		this.type = type;
		this.id = id;
		this.name = name;
		this.cardinality = cardinality;
	}
	
	public Part(String type, int id) {
		name = "Special";
		this.id = id;
		this.type = name;
	}

	@Override
	public String toString() {
		return "Part [type=" + type + ", id=" + id + ", name=" + name + ", cardinality=" + cardinality + "]";
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + id;
		result = prime * result + ((name == null) ? 0 : name.hashCode());
		result = prime * result + ((type == null) ? 0 : type.hashCode());
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		Part other = (Part) obj;
		if (id != other.id)
			return false;
		if (name == null) {
			if (other.name != null)
				return false;
		} else if (!name.equals(other.name))
			return false;
		if (type == null) {
			if (other.type != null)
				return false;
		} else if (!type.equals(other.type))
			return false;
		return true;
	}

	public String gettype() {
		return type;
	}

	public void settype(String type) {
		this.type = type;
	}

	public int getId() {
		return id;
	}

	public void setId(int id) {
		this.id = id;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}
	

}
