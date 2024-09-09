import java.net.Socket;
import java.net.ServerSocket;
import java.text.MessageFormat;
import java.io.IOException;
import java.util.HashMap;

public class Server {

    private static final String host = "localhost";
    private static final int port = 50001;

    private HashMap<String, ClientHandler> clients = new HashMap<String, ClientHandler>();

    public static void main(String[] args) throws IOException {
        System.out.println(MessageFormat.format("Starting server at {0}:{1}...", host, port));
        SeverSocket serverSocket = new ServerSocket(port);
        int numClients = 0;

        while (true) {
            Socket clientSocket = serverSocket.accpet();

            ClientHandler clientHandler = new ClientHandler(clientSocket);
            clients.put(Integer.toString(numClients), clientHandler);
            numClients++;
            new Thread(clientHandler).start();

        }
    }


    public class ClientHandler implements Runnable {
        
        public ClientHandler(Socket socket) {
            Socket socket = socket;
            PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true);
            BufferedReader in = new BufferedReader(
                    new InputStreamReader(clientSocket.getInputStream()));
        }
    }

}

