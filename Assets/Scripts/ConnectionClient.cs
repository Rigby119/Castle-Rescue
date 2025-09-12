using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;
using TMPro;

[System.Serializable]
public class AdjData
{
    public int x;
    public int y;
    public string direction;
    public int state;
}

[System.Serializable]
public class StepData
{
    public int width;
    public int height;
    public List<int> fire;
    public List<int> agents;
    public List<int> pois;
    public List<AdjData> walls;
    public List<AdjData> doors;
    public object gameStatus;
}

public class ConnectionClient : MonoBehaviour
{
    public string stepURL = "http://localhost:5000/step";
    public string resetURL = "http://localhost:5000/reset";

    public GameObject firePrefab;
    public GameObject smokePrefab;
    public GameObject[] agentPrefabs;
    public GameObject poiPrefab;

    public GameObject doorOpenPrefab;
    public GameObject doorClosedPrefab;

    public Material wallDamagedMaterial;
    public Material wallMaterial;

    private Dictionary<string, GameObject> wallObjects = new Dictionary<string, GameObject>();
    private Dictionary<string, GameObject> doorObjects = new Dictionary<string, GameObject>();

    private List<GameObject> spawnedFires = new List<GameObject>();
    private List<GameObject> spawnedPois = new List<GameObject>();
    private GameObject[] agentObjects;

    public TMP_Text resumenText;
    private int pasoActual = 0;

    private int agentCount = 6;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        // Inicializar diccionarios con objetos existentes
        GameObject[] walls = GameObject.FindGameObjectsWithTag("Wall");
        GameObject[] doors = GameObject.FindGameObjectsWithTag("Door");

        foreach (GameObject wall in walls)
        {
            // Asumiendo que el nombre del objeto sigue el formato "x,y,direction"
            wallObjects[wall.name] = wall;
        }

        foreach (GameObject door in doors)
        {
            doorObjects[door.name] = door;
        }

        agentObjects = new GameObject[agentCount];
        StartCoroutine(GetStep());
    }

    public void NextStep()
    {
        StartCoroutine(GetStep());
    }

    void RenderStep(StepData data)
    {
        Quaternion rotacion = Quaternion.identity * Quaternion.Euler(0, 180, 0);

        foreach (var obj in spawnedFires)
            Destroy(obj);
        spawnedFires.Clear();

        foreach (var obj in spawnedPois)
            Destroy(obj);
        spawnedPois.Clear();

        bool[] agentPlaced = new bool[agentCount];

        for (int y = 0; y < data.height; y++)
        {
            for (int x = 0; x < data.width; x++)
            {
                int idx = y * data.width + x;

                int posX = x * 10 - 10;
                int posY = (5 - y) * 10 - 40;

                // Fuego
                if (data.fire[idx] == 2)
                    spawnedFires.Add(Instantiate(firePrefab, new Vector3(posX, 0, posY), rotacion));

                if (data.fire[idx] == 1)
                    spawnedFires.Add(Instantiate(smokePrefab, new Vector3(posX, 0, posY), rotacion));

                // POI
                if (data.pois[idx] == 1)
                    spawnedPois.Add(Instantiate(poiPrefab, new Vector3(posX, 0, posY), rotacion));

                // Agente
                int agentId = data.agents[idx];
                if (agentId > 0 && agentId <= agentCount)
                {
                    int agentIndex = agentId - 1;
                    agentPlaced[agentIndex] = true;
                    Vector3 pos = new Vector3(posX, 0, posY);

                    if (agentObjects[agentIndex] == null)
                    {
                        agentObjects[agentIndex] = Instantiate(agentPrefabs[agentIndex], pos, rotacion);
                    }
                    else
                    {
                        agentObjects[agentIndex].transform.position = pos;
                        agentObjects[agentIndex].SetActive(true);
                    }
                }
            }
        }

        // Actualizar paredes - solo cambio de material y visibilidad
        foreach (var wall in data.walls)
        {
            string wallKey = $"{wall.x},{wall.y},{wall.direction}";
            if (wallObjects.TryGetValue(wallKey, out GameObject wallObj))
            {
                if (wall.state == 1)
                {
                    wallObj.SetActive(false);
                }
                else
                {
                    wallObj.SetActive(true);
                    wallObj.GetComponent<Renderer>().material = 
                        wall.state == 2 ? wallDamagedMaterial : wallMaterial;
                }
            }
        }

        // Actualizar puertas - solo cambio de prefab
        foreach (var door in data.doors)
        {
            string doorKey = $"{door.x},{door.y},{door.direction}";
            if (doorObjects.TryGetValue(doorKey, out GameObject doorObj))
            {
                if ((door.state == 1 && doorObj.name.Contains("Open")) || 
                    (door.state == 2 && doorObj.name.Contains("Closed")))
                {
                    Vector3 pos = doorObj.transform.position;
                    Quaternion rot = doorObj.transform.rotation;
                    GameObject newDoorObj = Instantiate(
                        door.state == 1 ? doorClosedPrefab : doorOpenPrefab, 
                        pos, 
                        rot
                    );
                    newDoorObj.name = doorObj.name;  // Mantener el nombre original
                    Destroy(doorObj);
                    doorObjects[doorKey] = newDoorObj;
                }
            }
        }

        // Al final de RenderStep
        int fuegos = data.fire.FindAll(f => f == 2).Count;
        int humos = data.fire.FindAll(f => f == 1).Count;
        int pois = data.pois.FindAll(p => p == 1).Count;
        int agentes = 0;
        foreach (int a in data.agents)
        {
            if (a > 0) agentes++;
        }

        // Construir el resumen
        string resumen = $"Paso: {pasoActual}\n" +
                        $"Fuegos: {fuegos}\n" +
                        $"Humos: {humos}\n" +
                        $"POIs: {pois}\n" +
                        $"Agentes: {agentes}";

        // Mostrar en TMP si está asignado
        if (resumenText != null)
        {
            resumenText.text = resumen;
        }

    }

    private Quaternion GetRotationFromDirection(string direction)
    {
        switch (direction)
        {
            case "N": return Quaternion.Euler(0, 0, 0);
            case "S": return Quaternion.Euler(0, 180, 0);
            case "E": return Quaternion.Euler(0, 90, 0);
            case "W": return Quaternion.Euler(0, 270, 0);
            default: return Quaternion.identity;
        }
    }

    public void ResetModel()
    {
        StartCoroutine(ResetRequest());
        pasoActual = 0;
    }

    IEnumerator ResetRequest()
    {
        UnityWebRequest www = UnityWebRequest.PostWwwForm(resetURL, "");
        yield return www.SendWebRequest();

        if (www.result == UnityWebRequest.Result.Success)
        {
            // Restaurar todas las paredes
            foreach (var wallObj in wallObjects.Values)
            {
                if (wallObj != null)
                {
                    wallObj.SetActive(true);
                    wallObj.GetComponent<Renderer>().material = wallMaterial;
                }
            }
            StartCoroutine(GetStep());
        }
        else
        {
            Debug.LogError("Error: " + www.error);
        }
    }

    IEnumerator GetStep()
    {
        UnityWebRequest www = UnityWebRequest.Get(stepURL);
        yield return www.SendWebRequest();

        if (www.result == UnityWebRequest.Result.Success)
        {
            string json = www.downloadHandler.text;
            StepData data = JsonUtility.FromJson<StepData>(json);

            pasoActual++;
            RenderStep(data);
        }
        else
        {
            Debug.LogError("Error: " + www.error);
        }
    }
}
