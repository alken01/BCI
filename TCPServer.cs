using System;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

public class TcpClientScript : MonoBehaviour
{
    private TcpClient client;
    private NetworkStream stream;
    private byte[] receiveBuffer;
    private string receivedData;

    public string serverIp = "192.168.0.100";
    public int serverPort = 42069;

    private void Start()
    {
        client = new TcpClient(serverIp, serverPort);
        stream = client.GetStream();
        receiveBuffer = new byte[1024];
        receivedData = "";
    }

    private void Update()
    {
        if (client.Connected)
        {
            if (stream.DataAvailable)
            {
                int bytesRead = stream.Read(receiveBuffer, 0, receiveBuffer.Length);
                receivedData += Encoding.UTF8.GetString(receiveBuffer, 0, bytesRead);
            }

            if (receivedData != "")
            {
                Debug.Log("Server response: " + receivedData);
                receivedData = "";
            }

            if (Input.GetKeyUp(KeyCode.Return))
            {
                string message = Console.ReadLine();

                if (message != "")
                {
                    byte[] messageBytes = Encoding.UTF8.GetBytes(message);
                    stream.Write(messageBytes, 0, messageBytes.Length);

                    Debug.Log("Sent message: " + message);

                    if (message == "end")
                    {
                        client.Close();
                    }
                }
            }
        }
    }

    private void OnApplicationQuit()
    {
        client.Close();
    }
}
