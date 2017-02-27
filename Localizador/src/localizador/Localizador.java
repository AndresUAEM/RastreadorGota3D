/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package localizador;

import py4j.GatewayServer;

import fiji.plugin.trackmate.Logger;
import fiji.plugin.trackmate.Model;
import fiji.plugin.trackmate.SelectionModel;
import fiji.plugin.trackmate.Settings;
import fiji.plugin.trackmate.Spot;
import fiji.plugin.trackmate.TrackMate;
import fiji.plugin.trackmate.TrackModel;
import fiji.plugin.trackmate.detection.DogDetectorFactory;
import fiji.plugin.trackmate.tracking.LAPUtils;
import fiji.plugin.trackmate.tracking.sparselap.SparseLAPTrackerFactory;
import fiji.plugin.trackmate.visualization.hyperstack.HyperStackDisplayer;
import ij.ImagePlus;
import ij.io.Opener;
import ij.plugin.FolderOpener;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import javax.swing.JFrame;
import javax.swing.JOptionPane;

/**
 *
 * @author andres
 */
public class Localizador {

    
    private double diametro;
    private double threshold;
    private double distancia;
    private String ruta;
    
    private ImagePlus imagenes;
    private double alturas[][];
    
    //private static List<Track> tracks;
    public Localizador()
    {
        
    }
    
    public void abrir()
    {
        File folder = new File(ruta);
        try
        {
            FolderOpener folderOpener=new FolderOpener();
            folderOpener.openAsVirtualStack(true);
            folderOpener.sortFileNames(true);
            File[] files = folder.listFiles();
            if (files.length==2)
            {
                for (File file : files)
                {
                    if (file.getAbsolutePath().endsWith(".tif")||file.getAbsolutePath().endsWith(".tiff"))//Abrir hyperstack
                    {
                        Opener opener=new Opener();
                        imagenes = opener.openImage(file.getAbsolutePath());
                    }
                    else//Leer alturas
                    {
                        try (BufferedReader br = new BufferedReader(new FileReader(file.getAbsolutePath())))
                        {
                            String sCurrentLine;
                            List<String[]> myList = new ArrayList<>();
                            while ((sCurrentLine = br.readLine()) != null)
				myList.add(sCurrentLine.split(","));
                            alturas=new double[myList.size()][myList.get(0).length];
                            for (int i=0;i<alturas.length;i++)
                            {
                                String[] lista=myList.get(i);
                                for (int j=0;j<alturas[0].length;j++)
                                {
                                    alturas[i][j]=Double.parseDouble(lista[j]);
                                }
                            }                           

                        }
                        catch (IOException ex)
                        {
                            error("Falta el archivo de alturas!!!"); 
                        }

                    }//System.out.println(imagenes[i].getNFrames());
                }
            }
            else
            {
                error("Error en la carpeta!!!");
            }
        }
        catch(NullPointerException ex)
        {
            error("La carpeta '"+ruta+"' no existe");
            
        }
        //imagenes.getCalibration().pixelDepth=alturas[alturas.length/2]-alturas[alturas.length/2-1];
        //double zVox = imagenes.getCalibration().pixelDepth;
        //System.out.println(zVox);
        
    }
    
    public void establecerParametros(String carpeta,double diam,double umbral,double distMax)
    {
        ruta=carpeta;
        diametro=diam;
        threshold=umbral;
        distancia=distMax;
        System.out.println(ruta);
    }
    
    public void mostrar()
    {
        Model m=new Model();
        SelectionModel sm=new SelectionModel(m);
        HyperStackDisplayer disp=new HyperStackDisplayer(m,sm,imagenes);
        disp.render();
        disp.refresh();
    }
    
    private static void error(String texto)
    {
        JFrame frame = new JFrame("Error");
        JOptionPane.showMessageDialog(frame,texto,"Error",JOptionPane.ERROR_MESSAGE);
        //System.exit(0);
    }
    
    public List<List<double[]>> localizar()
    {
        Model model=new Model();//Almacena los resultados del rastreo.
        model.setLogger(Logger.IJ_LOGGER);
        
        Settings settings=new Settings();//Configuración de TrackMate (Algoritmo e imágenes).
        settings.detectorFactory=new DogDetectorFactory();
        settings.detectorSettings = new HashMap();
        settings.detectorSettings.put("DO_SUBPIXEL_LOCALIZATION",false);
        settings.detectorSettings.put("RADIUS", 0.5*diametro);
        settings.detectorSettings.put("TARGET_CHANNEL",1);
        settings.detectorSettings.put("THRESHOLD",threshold);
        settings.detectorSettings.put("DO_MEDIAN_FILTERING",false);
        
        settings.trackerFactory = new SparseLAPTrackerFactory();
        settings.trackerSettings = LAPUtils.getDefaultLAPSettingsMap();// almost good enough
        settings.trackerSettings.put("LINKING_MAX_DISTANCE", distancia);
        settings.trackerSettings.put("GAP_CLOSING_MAX_DISTANCE", 2.0);
        settings.trackerSettings.put("MAX_FRAME_GAP", 1);
        int val=0;
        settings.setFrom(imagenes);
        List<List<double[]>> tracks=new ArrayList<>();
        TrackMate trackmate=new TrackMate(model,settings);//Se encarga de localizar las partículas.
        if (!trackmate.process()){error("Error al procesar!"+trackmate.getErrorMessage());}
        else if (!trackmate.checkInput()){error("Error en el stack!"+trackmate.getErrorMessage());}
        else
        {
            System.out.println("Guardando...");
            TrackModel trackModel=model.getTrackModel();
            model.getLogger().log("Found " + (trackModel.nTracks(true)) + " tracks.");
            for (int id : trackModel.trackIDs(true))
            {
                //model.getLogger().log("Track ID: "+id);
                List<double[]> track=new ArrayList<>();
                double deltaZ=imagenes.getCalibration().pixelDepth;
                
                for (Spot spot : model.getTrackModel().trackSpots(id))
                {    
                    double punto[]=new double[4];
                    //Fetch spot features directly from spot.
                    punto[0] = spot.getFeature("POSITION_X")/diametro;//Posicion x en micras.
                    punto[1] = spot.getFeature("POSITION_Y")/diametro;//Posicion y en micras.
                    punto[2] = spot.getFeature("POSITION_Z")/deltaZ;//Numero de plano
                    punto[3] = spot.getFeature("FRAME");
                    track.add(punto);
                }
                tracks.add(track);
            }
            
        }
        return tracks;
    }
    
    public void setVoxelSize()
    {
        double[] difs = new double[alturas.length];
        int c=2;
        double sumaZ=0;
        for (double z : alturas[0])sumaZ+=z;
        double anterior=sumaZ/(alturas[0].length);
        for (int i=1;i<alturas.length;i++)
        {
            sumaZ=0;
            for (double z : alturas[i])sumaZ+=z;
            double media=sumaZ/(alturas[0].length);
            if (media>=0)
            {
                difs[i]=media-anterior;
            }
            else
            {
                c++;
            }
            anterior=media;
        }
        double suma=0;
        for (int i=c;i<alturas.length;i++)suma+=difs[i];
        double depth=suma/(difs.length-c);
        imagenes.getCalibration().pixelHeight=1;
        imagenes.getCalibration().pixelWidth=1;
        imagenes.getCalibration().pixelDepth=depth;
        double x=imagenes.getCalibration().pixelWidth;
        double y=imagenes.getCalibration().pixelHeight;
        double z=imagenes.getCalibration().pixelDepth;
        System.out.println("Tamano de pixel: ("+x+" , "+y+" , "+z+")");
        
    }

    /**
     * @param args the command line arguments
     */
        public static void main(String[] args) {
        //myTest app = new myTest();
        // app is now the gateway.entry_point
        GatewayServer server = new GatewayServer(new Localizador());
        server.start();
        System.out.println("JVM Track inicializada");
    }
}
