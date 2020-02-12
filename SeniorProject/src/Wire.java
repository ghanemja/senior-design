
import java.util.HashMap;

public class Wire {

	private int id;
	private HashMap<Integer, String> connections = new HashMap<Integer, String>();
	
	public Wire(int id) {
		this.id = id;
	}

	public int getId() {
		return id;
	}

	@Override
	public String toString() {
		return "Wire [id=" + id + ", connections=" + connections + "]";
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + ((connections == null) ? 0 : connections.hashCode());
		result = prime * result + id;
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
		Wire other = (Wire) obj;
		if (connections == null) {
			if (other.connections != null)
				return false;
		} else if (!connections.equals(other.connections))
			return false;
		if (id != other.id)
			return false;
		return true;
	}

	public void setId(int id) {
		this.id = id;
	}

	public HashMap<Integer, String> getConnections() {
		return connections;
	}

	public void setConnections(HashMap<Integer, String> connections) {
		this.connections = connections;
	}
	
	public void addConn(int partId, String name) {
		connections.put(partId, name);
	}
}
