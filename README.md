# openstriato-python-commandline
My contribution to the project OpenStriato, a python package to use "openstriato -arg argument...". This package will be used to control the Raspberry with NFC tags.
# Static Analysis
This project uses PyLint. To use PyLint install the package (pip install pylint) and run<br />
<code>$pylint -f parseable openstriato.py > openstriato.out</code>
# Tests
This project uses Nose. To use Nose install the package (pip install nose) and run<br />
<code>$nosetests -v file.py</code><br />
You can edit XML reports in JUnit and Cobertura. For example, you can associate a continuous integration tool. Just run<br />
<code>$nosetests -v file.py -xunit -xcoverage</code>
# The Raspberry advices!
To be able to work the NFC shield on the Raspberry Pi (mine is model Bv2), several things are good to know.
The basic is described here : http://www.framboise314.fr/jai-teste-pour-vous-la-carte-explore-nfc-delement-14-12/#comment-23647
But the card_polling sources are not enough to make these commands to work. You have to do
* Since kernel 3.18 (Beginning 2015)
The card-polling sample works on Raspbery Pi 2 with kernel 3.18, but there is a missing initialization after the line 329 of the file NxpRdLib_PublicRelease/comps/phbalReg/src/R_Pi_spi/phbalReg_R_Pi_spi.c :
<pre>
phStatus_t phbalReg_R_Pi_spi_Exchange(
phbalReg_R_Pi_spi_DataParams_t * pDataParams, 
uint16_t wOption, 
uint8_t * pTxBuffer, 
uint16_t wTxLength, 
uint16_t wRxBufSize, 
uint8_t * pRxBuffer, 
uint16_t * pRxLength
)
{
struct spi_ioc_transfer spi ;
<b>memset(&spi,0,sizeof(spi));   // add missing initialization</b>
</pre>
* For the python to get the result of the pooling, add fflush(stdout) in the polling loop in main.c, line 278
<pre>
        else
        {
            printf("No card or Tag detected\n");
        }
		fflush(stdout); // adding fflush to use python
        sleep(1);
    }

    phhalHw_FieldOff(pHal);
    return 0;
</pre>
